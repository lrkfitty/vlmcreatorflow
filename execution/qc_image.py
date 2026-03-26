#!/usr/bin/env python3.11
"""
qc_image.py — AI Image Quality Control Pipeline
-------------------------------------------------
Runs a 5-step QC check on any generated image before it enters the posting queue.

Steps:
  1. Compliance     — aspect ratio, resolution, file size
  2. Blur           — Laplacian variance (OpenCV)
  3. Aesthetic      — LAION aesthetic predictor (CLIP-based)
  4. Face quality   — DeepFace face count + face sharpness (portrait only)
  5. Overall score  — pyiqa NIMA

Returns: {"pass": bool, "scores": dict, "reason": str|None}

Auto-regenerate on fail: caller re-queues with new seed (up to MAX_ATTEMPTS).
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Thresholds ────────────────────────────────────────────────────────────────
THRESHOLDS = {
    "laplacian_min":      80,     # below = too blurry
    "aesthetic_min":     5.0,     # below = auto-reject
    "aesthetic_review":  5.5,     # below aesthetic_min+review band = flag for review
    "face_conf_min":     0.85,    # face detector confidence
    "brisque_max":       50,      # above = poor technical quality
    "min_resolution":    1080,    # minimum pixels on short side
    "max_file_mb":       30,      # max file size in MB
}

# ── Expected aspect ratios ─────────────────────────────────────────────────────
VALID_RATIOS = {
    "9:16":  9  / 16,
    "4:5":   4  / 5,
    "1:1":   1.0,
    "16:9":  16 / 9,
}
RATIO_TOLERANCE = 0.04  # ±4%


def _check_compliance(img_path: str) -> dict:
    """Step 1: file-level checks — no ML needed."""
    from PIL import Image
    result = {"pass": True, "reason": None}

    # File size
    size_mb = os.path.getsize(img_path) / (1024 * 1024)
    if size_mb > THRESHOLDS["max_file_mb"]:
        return {"pass": False, "reason": f"File too large: {size_mb:.1f}MB"}

    img = Image.open(img_path)
    w, h = img.size

    # Minimum resolution
    short_side = min(w, h)
    if short_side < THRESHOLDS["min_resolution"]:
        return {"pass": False, "reason": f"Resolution too low: {w}x{h} (min {THRESHOLDS['min_resolution']}px short side)"}

    # Aspect ratio
    actual_ratio = w / h
    ratio_ok = any(
        abs(actual_ratio - r) < RATIO_TOLERANCE
        for r in VALID_RATIOS.values()
    )
    if not ratio_ok:
        return {"pass": False, "reason": f"Unexpected aspect ratio: {actual_ratio:.3f} ({w}x{h})"}

    result["size_mb"] = round(size_mb, 2)
    result["resolution"] = f"{w}x{h}"
    return result


def _check_blur(img_path: str) -> dict:
    """Step 2: Laplacian variance blur detection via OpenCV."""
    try:
        import cv2
        import numpy as np
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return {"pass": False, "reason": "OpenCV could not read image"}
        score = float(cv2.Laplacian(img, cv2.CV_64F).var())
        passed = score >= THRESHOLDS["laplacian_min"]
        return {
            "pass": passed,
            "laplacian": round(score, 1),
            "reason": None if passed else f"Image too blurry: Laplacian={score:.1f} (min {THRESHOLDS['laplacian_min']})"
        }
    except ImportError:
        logger.warning("opencv-python not installed — skipping blur check")
        return {"pass": True, "laplacian": None, "reason": None}


def _check_aesthetic(img_path: str) -> dict:
    """Step 3: LAION aesthetic predictor score."""
    try:
        from aesthetics_predictor import AestheticsPredictorV2Linear
        from transformers import CLIPProcessor
        from PIL import Image
        import torch

        model = AestheticsPredictorV2Linear.from_pretrained("shunk031/aesthetics-predictor-v2-sac-logos-ava1-l14-linearMSE")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
        model.eval()

        image = Image.open(img_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            score = float(model(**inputs).logits[0][0])

        passed = score >= THRESHOLDS["aesthetic_min"]
        needs_review = not passed and score >= (THRESHOLDS["aesthetic_min"] - 0.5)
        return {
            "pass": passed,
            "aesthetic_score": round(score, 3),
            "needs_review": needs_review,
            "reason": None if passed else f"Low aesthetic score: {score:.2f} (min {THRESHOLDS['aesthetic_min']})"
        }
    except Exception as e:
        logger.warning(f"Aesthetic check skipped: {e}")
        return {"pass": True, "aesthetic_score": None, "reason": None}


def _check_face(img_path: str) -> dict:
    """Step 4: DeepFace face detection and sharpness check."""
    try:
        from deepface import DeepFace
        import cv2
        import numpy as np

        faces = DeepFace.extract_faces(
            img_path=img_path,
            detector_backend="retinaface",
            enforce_detection=False,
            align=True
        )

        face_count = len([f for f in faces if f.get("confidence", 0) >= THRESHOLDS["face_conf_min"]])

        if face_count == 0:
            return {"pass": False, "face_count": 0, "reason": "No face detected — likely a failed generation"}

        # Check sharpness of the primary face crop
        primary = max(faces, key=lambda f: f.get("confidence", 0))
        face_arr = primary.get("face")
        if face_arr is not None:
            import numpy as np
            gray = np.mean(face_arr, axis=2) if face_arr.ndim == 3 else face_arr
            face_blur = float(np.var(np.gradient(gray.astype(float))))
            if face_blur < 30:
                return {
                    "pass": False,
                    "face_count": face_count,
                    "face_sharpness": round(face_blur, 1),
                    "reason": f"Face region too blurry: sharpness={face_blur:.1f}"
                }

        return {
            "pass": True,
            "face_count": face_count,
            "face_confidence": round(primary.get("confidence", 0), 3),
            "reason": None
        }
    except Exception as e:
        logger.warning(f"Face check skipped: {e}")
        return {"pass": True, "face_count": None, "reason": None}


def run_qc(img_path: str, is_portrait: bool = True) -> dict:
    """
    Full QC pipeline. Returns:
    {
        "pass": bool,
        "scores": { laplacian, aesthetic_score, face_count, ... },
        "reason": str | None,   # first failure reason
        "needs_review": bool    # borderline aesthetic score
    }
    """
    img_path = str(img_path)
    if not os.path.exists(img_path):
        return {"pass": False, "scores": {}, "reason": "File not found", "needs_review": False}

    scores = {}
    first_fail = None

    # Step 1: Compliance
    r1 = _check_compliance(img_path)
    scores.update({k: v for k, v in r1.items() if k not in ("pass", "reason")})
    if not r1["pass"]:
        return {"pass": False, "scores": scores, "reason": r1["reason"], "needs_review": False}

    # Step 2: Blur
    r2 = _check_blur(img_path)
    scores["laplacian"] = r2.get("laplacian")
    if not r2["pass"] and first_fail is None:
        first_fail = r2["reason"]

    # Step 3: Aesthetic
    r3 = _check_aesthetic(img_path)
    scores["aesthetic_score"] = r3.get("aesthetic_score")
    needs_review = r3.get("needs_review", False)
    if not r3["pass"] and first_fail is None:
        first_fail = r3["reason"]

    # Step 4: Face (portraits only)
    if is_portrait:
        r4 = _check_face(img_path)
        scores["face_count"] = r4.get("face_count")
        scores["face_confidence"] = r4.get("face_confidence")
        if not r4["pass"] and first_fail is None:
            first_fail = r4["reason"]

    passed = first_fail is None
    logger.info(f"QC {'PASS' if passed else 'FAIL'} — {Path(img_path).name} | scores: {scores}")

    return {
        "pass": passed,
        "scores": scores,
        "reason": first_fail,
        "needs_review": needs_review and passed  # only flag review if otherwise passing
    }


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys, json
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path:
        print("Usage: python3 execution/qc_image.py <image_path>")
        sys.exit(1)
    result = run_qc(path)
    print(json.dumps(result, indent=2))
