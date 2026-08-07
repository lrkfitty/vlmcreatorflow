#!/opt/homebrew/bin/python3.11
"""
VLM B2B Niche — 9-Grid Instagram Batch Generator (Multi-Niche & Multi-Cast)
Creates professional, high-converting posts featuring the entire VLM cast 
acting as examples of successful local business owners (Roofing, Construction, 
Plumbers, Landscaping, Remodel).

Outputs directly into output/users/VLM/Instagram for auto_poster.py.
"""
import os, sys, json, time, shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()
from execution.generate_image import generate_image_from_prompt

BASE = Path(__file__).parent.parent

# ── Character Refs ───────────────────────────────────────────────
ASSETS = BASE / "assets" / "AI Content Creators"
FRIENDS = ASSETS / "Friends"

NEO_REF       = FRIENDS / "Mens Friends" / "Neo.png"
TYRIE_REF     = FRIENDS / "Tyrie Master" / "Tyrie Hero" / "Tyrie.png"
SHAY_REF      = ASSETS / "Shay.So.Fine" / "SHAY STOCK Photo" / "Shay blonde bob front .png"
ANGEIL_REF    = FRIENDS / "Angeil Master " / "Angeil Hero image" / "Angeil.png"
JAZMINE_REF   = FRIENDS / "Black Influencer Models" / "Jazmine.jpg"
FRANNIE_REF   = FRIENDS / "Latina Influencers" / "Franscesca .jpg"
SOPHIA_REF    = FRIENDS / "White Influencers" / "Sophia 1.png"

# Optional clothing references for the guys
NEO_CLOTH     = FRIENDS / "Mens Friends" / "Neo Outfits" / "Mens clothing" / "Louis Vutton Brown fit .png"
TYRIE_CLOTH   = FRIENDS / "Tyrie Master" / "Tyrie Clothing" / "Monaco Outfit.jpg"

OUTPUT = BASE / "output" / "users" / "VLM" / "Instagram"

# ── Descriptions ───────────────────────────────────────────────
CAST_DESCS = {
    "Tyrie":   "The subject is a tall, heavily muscular Black man with full-body tattoos across both arms, chest, and back. Athletic build, sharp fade haircut.",
    "Neo":     "The subject is a light-skinned Black man with a well-groomed beard, medium build, sharp confident demeanor.",
    "Shay":    "Beautiful Black woman with a signature shoulder-length blonde bob, melanin-rich brown skin.",
    "Angeil":  "Beautiful Black woman, melanin-rich skin, dark hair, modelesque corporate frame.",
    "Jazmine": "Stunning Black woman, warm brown skin, long natural hair, radiates professional confidence.",
    "Frannie": "Beautiful Latina woman, warm olive complexion, high cheekbones, business executive posture.",
    "Sophia":  "Beautiful white woman, light skin, effortless chic, commanding professional presence."
}

def scene(desc, prompt_env):
    """Build a cinematic prompt for B2B VLM."""
    return f"{desc} {prompt_env} Ultra-realistic. 4K. Aspect ratio 4:5. No text."

# ── The Multi-Niche 9-Grid Strategy ──────────────────────────────────────────
# Mixes construction, roofing, general contracting, plumbing, electricians, remodel, landscaping.
# Features different characters leading the visual narrative.

CAROUSELS = [
    {
        "id": "vlm_b2b_1_roofing",
        "cast": "Tyrie",
        "cast_desc": CAST_DESCS["Tyrie"],
        "ref": TYRIE_REF,
        "outfit": TYRIE_CLOTH,
        "caption": (
            "Still relying on shared leads to grow your roofing business? 🛑\n\n"
            "When homeowners need a $15k+ roof replacement, the first thing they check is your website. "
            "If it looks like it was built in 2012, or worse—you don't have one—you're handing money "
            "straight to your competitors.\n\n"
            "At VLM, we build custom, high-converting digital storefronts that make you the undeniable authority in your city.\n\n"
            "Stop fighting for shared leads. Start owning your market.\n\n"
            "#roofinglife #roofingcontractor #roofingsales #localbusiness #webdesign #vlm"
        ),
        "shots": [
            scene(CAST_DESCS["Tyrie"],
                  "Epic cinematic photograph of this man standing in front of a massive high-end residential roofing project. "
                  "He is acting as the commanding owner of a multi-million dollar roofing company, holding a digital tablet. "
                  "Behind him: a sleek branded fleet truck, workers in the background. "
                  "Deep shadows, dramatic single-source key lighting. "
                  "Shot on ARRI Alexa, anamorphic lens. Cinematic.")
        ],
    },
    {
        "id": "vlm_b2b_2_construction",
        "cast": "Angeil",
        "cast_desc": CAST_DESCS["Angeil"],
        "ref": ANGEIL_REF,
        "outfit": None, # Let AI generate the outfit
        "caption": (
            "We took a look at 50 General Contractors in your area.\n"
            "45 had over 5+ reviews on Google.\n"
            "Only 12 had a website that actually worked on a mobile phone.\n\n"
            "Clients are researching multi-million dollar construction bids from their phones. "
            "If they can't find you, they find the GC who took 2 hours to set up a clean, modern site.\n\n"
            "We build sites that turn searches into massive contracts. DM us 'BUILD' to see a free custom mockup.\n\n"
            "#generalcontractor #constructioncompany #contractormarketing #leadgeneration #vlm"
        ),
        "shots": [
            scene(CAST_DESCS["Angeil"],
                  "Powerful cinematic photograph of this woman as the CEO of a massive commercial construction firm. "
                  "She is wearing a high-end tailored slate-grey suit paired with a premium white hardhat under her arm. "
                  "She stands confidently on a high-rise construction site at golden hour, framing steel in the background. "
                  "Warm sun flares, brass accents, premium aesthetic. "
                  "Shot on Sony A7RV, 85mm. Business editorial.")
        ],
    },
    {
        "id": "vlm_b2b_3_plumbing",
        "cast": "Neo",
        "cast_desc": CAST_DESCS["Neo"],
        "ref": NEO_REF,
        "outfit": NEO_CLOTH,
        "caption": (
            "How does a local plumbing company scale from 1 truck to a $5M/yr fleet? ⚙️\n\n"
            "It doesn't happen by accident. It happens because your digital presence is built to convert. "
            "When a pipe bursts at 2 AM, they don't ask friends for a referral. They Google it and click the site that looks the most trustworthy.\n\n"
            "Is your site the one they click?\n\n"
            "#plumbinglife #plumber #hvac #contractors #businessgrowth #vlm"
        ),
        "shots": [
            scene(CAST_DESCS["Neo"],
                  "Dramatic cinematic portrait of this man as the owner of a massive plumbing and HVAC local enterprise. "
                  "He is standing in a pristine, brilliantly lit supply warehouse in front of a row of perfectly branded modern service vans. "
                  "He looks directly into the camera with absolute authority. "
                  "Deep cinematic lighting, sharp details. The focus of an absolute professional. "
                  "Shot on 85mm lens, shallow depth of field.")
        ],
    },
    {
        "id": "vlm_b2b_4_remodel",
        "cast": "Frannie",
        "cast_desc": CAST_DESCS["Frannie"],
        "ref": FRANNIE_REF,
        "outfit": None,
        "caption": (
            "Your high-end remodels are beautiful. Does your brand reflect that? 🏡\n\n"
            "If you're charging $100k+ for kitchen and bath remodels, your digital front door cannot look cheap. "
            "Homeowners buy trust and aesthetics. If you look premium, you command premium pricing.\n\n"
            "We ensure your brand matches the exact quality of your craftsmanship.\n\n"
            "#homeremodel #interiordesign #contractorlife #premiumbrand #vlm"
        ),
        "shots": [
            scene(CAST_DESCS["Frannie"],
                  "Wide cinematic shot of this woman as the visionary owner of a luxury home remodeling company. "
                  "She stands in the center of a breathtaking, ultra-modern kitchen mid-renovation with marble slabs and architectural blueprints on an island. "
                  "She is wearing a stylish neutral-toned blazer and jeans. "
                  "Deep rich shadows, natural light pouring through massive windows. "
                  "Shot on ARRI, ultra-wide. High-end real estate meets luxury brand.")
        ],
    },
    {
        "id": "vlm_b2b_5_landscaping",
        "cast": "Shay",
        "cast_desc": CAST_DESCS["Shay"],
        "ref": SHAY_REF,
        "outfit": None,
        "caption": (
            "The old way: Drop $5k on home mailers and hope for the best.\n"
            "The VLM way: Build an undeniable local landscaping brand so affluent homeowners come directly to YOU. 🎯\n\n"
            "Stop fighting for $50 mows. Start landing $50k outdoor living and hardscape contracts by looking like the most premium operation in your county.\n\n"
            "#landscaping #hardscape #landscapedesign #businessowner #vlm"
        ),
        "shots": [
            scene(CAST_DESCS["Shay"],
                  "Epic wide cinematic image: this woman acting as the fierce CEO of a massive luxury landscaping architecture firm. "
                  "She is standing in front of a multi-million dollar luxury estate's manicured gardens, holding digital blueprints on an iPad. "
                  "Her outfit is sophisticated outdoor-business chic — earth tones, high-end boots. "
                  "Beautiful golden hour lighting hitting the greenery, cinematic blue sky. "
                  "Directional lighting. Deep, cinematic, editorial.")
        ],
    },
    {
        "id": "vlm_b2b_6_electrician",
        "cast": "Jazmine",
        "cast_desc": CAST_DESCS["Jazmine"],
        "ref": JAZMINE_REF,
        "outfit": None,
        "caption": (
            "In the electrical trade, Trust is the only currency. ⚡️\n\n"
            "Before they let you wire their custom home or commercial building, they walk through your digital front door. "
            "We build high-trust digital assets for master electricians who want to stop competing on price and start winning on authority.\n\n"
            "Let's elevate your electrical brand today. 🔌\n\n"
            "#electrician #electricalcontractor #tradesman #tradeswoman #vlm"
        ),
        "shots": [
            scene(CAST_DESCS["Jazmine"],
                  "Medium close-up shot of this woman as the boss of a large commercial electrical contracting firm. "
                  "She is standing on a vast commercial job site, electrical conduits running in the background. "
                  "She wears a sharp, fitted corporate polo and a premium hardhat, looking directly at the camera with an expression of absolute trust. "
                  "Industrial cinematic lighting, spark-like amber background flares. "
                  "Shot on 50mm, f/1.4.")
        ],
    },
    {
        "id": "vlm_b2b_7_ai_cost",
        "cast": "Sophia",
        "cast_desc": CAST_DESCS["Sophia"],
        "ref": SOPHIA_REF,
        "outfit": None,
        "caption": (
            "You don't need a $15,000 photoshoot to look like the most premium contractor in your state. 📸🚫\n\n"
            "We use cutting-edge AI and elite cinematic design to build your brand visuals in a fraction of the time and cost. "
            "Whether you're a GC, roofer, or landscaper, we generate a visual presence that puts you in a league of your own.\n\n"
            "Ready to stop looking like every other truck in town? Let's talk.\n\n"
            "#aiagency #marketingagency #aimarketing #localbusiness #vlm"
        ),
        "shots": [
            scene(CAST_DESCS["Sophia"],
                  "Cinematic portrait of this woman as a high-end AI tech agency director. "
                  "She is standing in a dark, ultra-modern tech studio. "
                  "Around her, floating holographic or digital display screens show stunning before-and-after brand transformations for local construction businesses. "
                  "Cool blue and clean white neon lighting. "
                  "High contrast, editorial style, magazine cover quality.")
        ],
    },
    {
        "id": "vlm_b2b_8_scale",
        "cast": "Neo",
        "cast_desc": CAST_DESCS["Neo"],
        "ref": NEO_REF,
        "outfit": NEO_CLOTH,
        "caption": (
            "Scaling from 1 crew to 5 crews doesn't happen by accident. 📈\n\n"
            "It happens because your local marketing funnel is ruthlessly efficient. "
            "It happens because clients see you everywhere—on Google, on Instagram, on Facebook—"
            "and you look like the most professional outfit in town.\n\n"
            "VLM is the growth partner that builds the digital foundation for your expansion.\n\n"
            "#businessscaling #tradebusiness #bluecollar #marketingstrategy #vlm"
        ),
        "shots": [
            scene(CAST_DESCS["Neo"],
                  "Cinematic wide shot of this man standing confidently on a high-rise balcony looking out over a sprawling city at morning light. "
                  "He is the architect of business scaling. He holds a sleek digital pad displaying market share analytics. "
                  "Cool morning light mixed with the warm amber of city sun rays. "
                  "The vibe is massive scale, growth, and dominion over a local market. "
                  "Ultra-realistic, cinematic.")
        ],
    },
    {
        "id": "vlm_b2b_9_mockup_cta",
        "cast": "Tyrie",
        "cast_desc": CAST_DESCS["Tyrie"],
        "ref": TYRIE_REF,
        "outfit": TYRIE_CLOTH,
        "caption": (
            "A message to the local contractors out there grinding it out every day 🔨:\n\n"
            "Your craftsmanship is 10/10, but your website says 3/10. "
            "I'm offering a FREE, custom-built mockup of a brand new homepage for your business. "
            "No strings attached. I just want to show you what's possible when your brand looks as good as your installs.\n\n"
            "DM me 'BUILD' and I'll send it over within 48 hours.\n\n"
            "#freeoffer #localbusiness #contractors #webdesign #vlm"
        ),
        "shots": [
            scene(CAST_DESCS["Tyrie"],
                  "Epic low-angle hero shot of this man looking directly into the camera with intense, trustworthy focus. "
                  "He is pointing directly at the viewer. "
                  "The background is a blur of a massive, successful contracting operation—trucks, equipment, blueprints. "
                  "Cinematic slow-motion energy. Strong shadows, highlighting his fierce authority. "
                  "Shot on 35mm, cinematic grade, motion implied.")
        ],
    }
]

def generate_vlm_batch():
    OUTPUT.mkdir(parents=True, exist_ok=True)

    # Support single-post regeneration from the reviewer
    regen_id = os.environ.get("VLM_REGEN_ID")
    posts_to_run = [p for p in CAROUSELS if not regen_id or p["id"] == regen_id]

    print(f"\n--- VLM B2B LOCAL BUSINESS BATCH GENERATOR ({len(posts_to_run)} Posts) ---")
    start_time = time.time()
    
    for i, post in enumerate(posts_to_run, 1):
        cid = post["id"]
        print(f"\n[{i}/{len(CAROUSELS)}] Generating: {cid} (Cast: {post['cast']})")
        
        json_path = OUTPUT / f"{cid}_carousel.json"
        if json_path.exists():
            print(f"Skipping {cid} — already generated.")
            continue
            
        success_images = []
        
        # Build assets list
        ref_path = str(post["ref"])
        assets = []
        if os.path.exists(ref_path):
            assets.append({"label": f"Cast: {post['cast']}", "path": ref_path})
        else:
            print(f"WARNING: Missing ref image: {ref_path}")
            
        if post.get("outfit") and os.path.exists(str(post["outfit"])):
            assets.append({"label": "Outfit: Primary", "path": str(post["outfit"])})
            
        # Generate each shot
        for s_idx, prompt_text in enumerate(post["shots"], 1):
            print(f"  Shot {s_idx}/{len(post['shots'])}...")

            prompt_data = {
                "positive_prompt": prompt_text,
                "negative_prompt": "blurry, low quality, cartoon, watermark, distorted, ugly, fake, illustration",
                "aspect_ratio": "4:5",
                "image_size": "4K",
                "assets": assets,
            }

            result = generate_image_from_prompt(
                prompt_data=prompt_data,
                output_folder=str(OUTPUT),
            )

            if result["status"] == "success" and result.get("image_path"):
                success_images.append(result["image_path"])
                # Clean up thumb auto-created by generate_image
                thumb = result["image_path"].replace(".jpg", "_thumb.jpg")
                if os.path.exists(thumb):
                    os.remove(thumb)
            else:
                print(f"  FAILED: {result.get('logs', 'unknown error')[-200:]}")
                
        # Save manifest mapping if we got images
        if success_images:
            manifest = {
                "id": cid,
                "created_at": datetime.now().isoformat(),
                "caption": post["caption"],
                "images": success_images,
                "outfit": str(post["outfit"]) if post.get("outfit") else "None"
            }
            with open(json_path, "w") as f:
                json.dump(manifest, f, indent=2)
            print(f"  Saved carousel manifest: {json_path.name}")
        else:
            print(f"  Skipped manifest for {cid} (no images succeeded).")
            
    elapsed = time.time() - start_time
    print(f"\n--- BATCH COMPLETE in {elapsed:.1f}s ---")

if __name__ == "__main__":
    generate_vlm_batch()
