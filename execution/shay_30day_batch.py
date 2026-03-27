"""
Shay.So.Fine — 30-Day Instagram Carousel Batch Generator  (MASTER REWRITE)
Every post has Shay + 1-4 friends. Master-level photography language throughout.
"""
import os, sys, json, time, shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()
from execution.generate_image import generate_image_from_prompt

BASE = Path(__file__).parent.parent

# ── Shay refs ────────────────────────────────────────────────────────────────
SHAY_BACK   = BASE / "assets/AI Content Creators/Shay.So.Fine/SHAY STOCK Photo/Shay blonde bob back.png"
SHAY_FRONT  = BASE / "assets/AI Content Creators/Shay.So.Fine/SHAY STOCK Photo/Shay blonde bob front .png"
SHAY_BUN    = BASE / "assets/AI Content Creators/Shay.So.Fine/SHAY STOCK Photo/Shay High Bun Back.png"

# ── Friend refs ───────────────────────────────────────────────────────────────
FRIENDS_DIR  = BASE / "assets/AI Content Creators/Friends/Black Influencer Models"
WHITE_DIR    = BASE / "assets/AI Content Creators/Friends/White Influencers"
LATINA_DIR   = BASE / "assets/AI Content Creators/Friends/Latina Influencers"
ANGEIL_HERO  = BASE / "assets/AI Content Creators/Friends/Angeil Master /Angeil Hero image/Angeil.png"
ANGEIL_EYES  = FRIENDS_DIR / "AngeilEyes.JPEG"

# Named friends with their ref files
FRIEND_REFS = {
    "Angeil":   [str(ANGEIL_HERO), str(ANGEIL_EYES)],
    "Jazmine":  [str(FRIENDS_DIR / "Jazmine.jpg")],
    "Carli":    [str(FRIENDS_DIR / "Carli.jpg")],
    "Sophia":   [str(WHITE_DIR / "Sophia 1.png")],
    "Saddie":   [str(WHITE_DIR / "Saddie 1.png")],
    "Frannie":  [str(LATINA_DIR / "Franscesca .jpg")],
    "Kayla":    [str(LATINA_DIR / "Kayla.jpg")],
    "Destiny":  [str(FRIENDS_DIR / "East African Rich Girl .jpg")],
    "Jen":      [str(WHITE_DIR / "Jen swim 1 .png")],
    "MixedBabe":[str(FRIENDS_DIR / "Pretty curly long mixed Girl .jpg")],
}

# ── Clothing / envs ──────────────────────────────────────────────────────────
OUTFITS_2026 = BASE / "assets/AI Content Creators/2026 Jan CLothing "
OUTFITS_INF  = BASE / "assets/AI Content Creators/Influencer CLothing "
ENVS         = BASE / "assets/AI Content Creators/Environments"
ENVS_2026    = OUTFITS_2026 / "Jan 2026 Enviroments"
OUTPUT       = BASE / "output/users/Shay/Instagram"

# ── Dynamic outfit pool — ALL Shay outfits, env subfolder excluded ────────────
def _collect_outfits(directory: Path, exclude_dirs: set = None) -> list:
    exts = {".jpg", ".jpeg", ".png"}
    exclude_dirs = exclude_dirs or set()
    results = []
    for f in directory.rglob("*"):
        if f.suffix.lower() not in exts or f.name.startswith("._"):
            continue
        if any(ex in f.parts for ex in exclude_dirs):
            continue
        results.append(f)
    return sorted(results)

SHAY_ALL_OUTFITS = (
    _collect_outfits(OUTFITS_2026, exclude_dirs={"Jan 2026 Enviroments"}) +
    _collect_outfits(OUTFITS_INF)
)

# Angeil uses Shay's massive 148-file library (not her own small 13-file folder)
ANGEIL_ALL_OUTFITS = SHAY_ALL_OUTFITS

# ── Character descriptions ────────────────────────────────────────────────────
SHAY_DESC = (
    "Beautiful Black woman with a signature shoulder-length blonde bob, melanin-rich brown skin with a natural luminous glow, "
    "modelesque proportions, confident and effortlessly stylish. She is the main subject — 'it girl' energy without trying."
)

FRIEND_DESCS = {
    "Angeil":    "Beautiful Black woman, melanin-rich skin, natural or styled dark hair, modelesque frame, glowing and magnetic.",
    "Jazmine":   "Stunning Black woman, warm brown skin, long natural hair, warm smile, radiates confidence and joy.",
    "Carli":     "Beautiful Black woman, deep warm complexion, striking features, fashion-forward energy.",
    "Sophia":    "Beautiful white woman, light skin, warm expression, effortless European chic.",
    "Saddie":    "Beautiful white woman, sun-kissed skin, relaxed confident energy, natural beauty.",
    "Frannie":   "Beautiful Latina woman, warm olive complexion, high cheekbones, full of life and warmth.",
    "Kayla":     "Beautiful Latina woman, rich dark hair, confident smile, vibrant energy.",
    "Destiny":   "Beautiful East African woman, stunning bone structure, tall and elegant.",
    "Jen":       "Beautiful white woman, athletic build, warm smile, girl-next-door meets luxury.",
    "MixedBabe": "Beautiful mixed woman, curly hair, warm complexion, effortlessly magnetic.",
}


def scene(shay, friends, camera, lens, light, env_detail, action, film="Kodak Portra 400 emulation, natural grain, lifted blacks"):
    """Build a master-level prompt for a scene with Shay + friends."""
    friend_count = len(friends)
    cast_total = 1 + friend_count
    friend_names = " and ".join(friends.keys())
    friend_descs = " ".join([f"{name}: {FRIEND_DESCS.get(name, 'beautiful woman, stylish')}." for name in friends.keys()])
    return (
        f"{camera}, {lens}. "
        f"{light} "
        f"CAST ({cast_total} people): {SHAY_DESC} {friend_descs} "
        f"{env_detail} "
        f"{action} "
        f"{film}. Aspect ratio 4:5."
    )


# ── 30 carousels ─────────────────────────────────────────────────────────────
CAROUSELS = [
    # DAYS 1-5: Shay + Angeil
    {
        "id": "maldives_lewk",
        "friends": {"Angeil": FRIEND_REFS["Angeil"]},
        "outfit": "OUTFITS_2026/Scrunch Marble.png",
        "env": "ENVS/Maldives Pier Vibes .jpg",
        "caption": "Maldives hit different when you show up with your girl 🌊\n\nThe water was warm. The fits were warmer.\n\n#shaysofine #maldives #travelbae #itgirl #softgirlera",
        "shots": [
            scene(SHAY_DESC, {"Angeil": None},
                  "Canon EOS R5", "85mm f/1.2L wide open at f/1.4",
                  "Overwater pier at golden hour — the Andaman sun at 18° above the horizon, pure warm backlight, turquoise water refracting upward fills.",
                  "Maldivian overwater pier — thatched bungalows stretching into the distance, the water beneath crystal clear to the sand below, horizon clean.",
                  "Shay stands at the pier railing, back to camera, blonde bob catching the backlight. Angeil stands beside her mirroring the pose, both looking out at the open ocean. Their arms just touching at the elbow — not posed, present."),
            scene(SHAY_DESC, {"Angeil": None},
                  "Canon EOS R5", "50mm f/2.0",
                  "Three-quarter front angle, both women slightly turning — ocean breeze, backlight creating rim separation on their hair.",
                  "Overwater bungalow railings behind them, turquoise water below in soft bokeh. A half-empty coconut on the ledge.",
                  "Shay has sunglasses pushed up into her blonde bob, laughing at something Angeil said. Angeil is mid-sentence, animated, hands slightly raised. Genuine candid moment."),
            scene(SHAY_DESC, {"Angeil": None},
                  "Canon EOS R5", "35mm f/4",
                  "Wide environmental — late golden hour, the sky deepening orange behind the bungalow row.",
                  "The full pier compound — overwater villas, the lagoon, the reef line in the distance, a boat wake catching the last light.",
                  "Both women sitting at the pier edge, feet dangling over the water, shoulder to shoulder. Wide enough to see the scale of paradise around them. The composition dwarfs them perfectly — small figures in an enormous beautiful world."),
        ],
    },
    {
        "id": "phi_phi_travel",
        "friends": {"Angeil": FRIEND_REFS["Angeil"]},
        "outfit": "OUTFITS_2026/Jamaicanshorts .jpg",
        "env": "ENVS_2026/Phi Phi islands .jpg",
        "caption": "Phi Phi islands said come back soon 🏝️ I said bet.\n\nBetter with your girl by your side 💅🏾\n\n#phiphi #thailand #travelbae #shaysofine #aiinfluencer",
        "shots": [
            scene(SHAY_DESC, {"Angeil": None},
                  "Leica Q3", "28mm f/2.0",
                  "Hard midday sun over the Andaman, direct overhead light softened by natural cloud scatter — clean fill on both faces.",
                  "Long-tail boat deck — dramatic limestone karsts rising 200m from emerald water, jungle-covered and sheer. Two other tourists blurred in the far background.",
                  "Shay at the boat's bow, back to camera, blonde bob catching the wind. Angeil stands beside her, turning to look over her shoulder at the karsts. Both in Jamaica shorts. The scale of the cliffs behind them is breathtaking."),
            scene(SHAY_DESC, {"Angeil": None},
                  "Leica Q3", "50mm f/1.4",
                  "Open shade under the boat canopy, soft diffused light, no harsh shadows — both faces perfectly lit.",
                  "Phi Phi emerald water visible through the boat's open side, another boat in the far distance.",
                  "Three-quarter shot — Shay has turned, one hand shading her eyes looking at something in the distance. Angeil leans on the railing beside her, smiling. The ease of two women on an adventure together."),
            scene(SHAY_DESC, {"Angeil": None},
                  "Leica Q3", "21mm f/5.6",
                  "Wide angle, blue sky, the full Phi Phi panorama.",
                  "Long-tail boat, the full karst formation, emerald water — the world at its most dramatically beautiful.",
                  "Both women small against the epic scale — standing at the prow, arms outstretched, Titanic energy but make it editorial. The karsts tower behind. The water glitters below."),
        ],
    },
    {
        "id": "night_out_chanel",
        "friends": {"Angeil": FRIEND_REFS["Angeil"]},
        "outfit": "OUTFITS_INF/NightOut /chanel Yess Nude Dress .jpg",
        "env": "ENVS/Colorfol Lounge Room .jpg",
        "caption": "She don't get dressed for you. She gets dressed for her 💅🏾\n\nAnd her girls.\n\n#nightout #shaysofine #chanelgirl #softgirlera #itgirl",
        "shots": [
            scene(SHAY_DESC, {"Angeil": None},
                  "Sony A7R V", "85mm f/1.4",
                  "Upscale lounge — warm amber sconce lighting from the walls, a single directional spot from above creating drama on faces. No flash, pure available light.",
                  "Colorful high-end lounge — velvet banquettes, art on the walls, other guests blurred beautifully behind them. Cocktails on the table.",
                  "Shay stands in the Chanel nude dress, back partially to camera, blonde bob sleek. Angeil beside her, looking directly at camera with quiet confidence. Shay is turning to say something to her — mid-conversation, totally unposed."),
            scene(SHAY_DESC, {"Angeil": None},
                  "Sony A7R V", "50mm f/1.4",
                  "Same warm lounge light — both faces caught in the warm amber, skin luminous, no harshness.",
                  "Lounge in background — soft bokeh of other guests, candlelight on tables.",
                  "Three-quarter shot — both women facing camera, Shay with hand on hip, Angeil with arms lightly crossed. Confident, beautiful, completely in their element. The main characters of this room."),
            scene(SHAY_DESC, {"Angeil": None},
                  "Sony A7R V", "35mm f/2.0",
                  "Slightly wider — the full lounge ambience visible, warm and rich.",
                  "The full lounge: art, velvet, dim intimate atmosphere. Other well-dressed guests in the background.",
                  "Shay mid-laugh, head back, Angeil watching her with a warm smile. The chemistry of two women who are genuinely close, genuinely having fun. Neither is performing."),
        ],
    },
    {
        "id": "amalfi_coast",
        "friends": {"Angeil": FRIEND_REFS["Angeil"]},
        "outfit": "OUTFITS_2026/Pink Brunch Villa .jpg",
        "env": "ENVS/Almafi Coast 1.jpg",
        "caption": "Amalfi had us questioning why we don't live here 🇮🇹\n\nThe views, the food, the fits — undefeated.\n\n#amalficoast #italy #travelbae #shaysofine #luxurytravel",
        "shots": [
            scene(SHAY_DESC, {"Angeil": None},
                  "Canon EOS R5", "85mm f/1.2",
                  "Italian morning light — warm Mediterranean sun at 30° from the right, golden and hard, creating dramatic shadows on the white terrace walls.",
                  "Amalfi Coast terrace — colorful cliffside village tumbling down to the Mediterranean below, lemon trees in terracotta pots at the terrace edge, a half-eaten breakfast on the table behind them.",
                  "Shay back to camera on the terrace railing, blonde bob in the breeze, pink brunch outfit catching the sun. Angeil beside her, facing three-quarter, sunglasses on, looking at the view. Their elbows touching. Two women in their most gorgeous selves."),
            scene(SHAY_DESC, {"Angeil": None},
                  "Canon EOS R5", "50mm f/1.8",
                  "Same Italian morning gold, front-lit — both faces warm and glowing.",
                  "Terrace railing, the sea below, cliffside architecture behind.",
                  "Shay has turned to face Angeil, hand on her arm, saying something. Angeil laughing in response. The conversation between two friends on the most beautiful terrace in the world."),
            scene(SHAY_DESC, {"Angeil": None},
                  "Canon EOS R5", "28mm f/5.6",
                  "Wide — the full terrace, the full coast, maximum context.",
                  "The Amalfi cliff-face, colorful houses stacked impossibly above and below, the blue Mediterranean stretching to the horizon.",
                  "Both women small at the railing, the enormous beautiful coast filling the frame. They are part of the landscape now. This is what freedom looks like."),
        ],
    },
    {
        "id": "beach_paradise",
        "friends": {"Angeil": FRIEND_REFS["Angeil"]},
        "outfit": "OUTFITS_INF/Montce Swim/Montce Mockup 1.png",
        "env": "ENVS_2026/Beach Paradise.jpg",
        "caption": "She showed up and the beach had no choice 🌴\n\nSame for her girl.\n\n#beachgirl #shaysofine #travelbae #bikinibabe #paradise",
        "shots": [
            scene(SHAY_DESC, {"Angeil": None},
                  "Sony A7 IV", "85mm f/1.8",
                  "Noon tropical sun — overhead hard light creating strong catchlights in the water and on their skin, fill from the white sand below.",
                  "White powder sand beach, turquoise water to the horizon, palm trees out of focus at the edge. No footprints in the sand around them — pristine.",
                  "Shay back to camera, blonde bob catching the overhead light, Montce swimsuit. Angeil walking beside her, slightly ahead, turning back to look at camera. Both leaving footprints in the wet sand."),
            scene(SHAY_DESC, {"Angeil": None},
                  "Sony A7 IV", "135mm f/1.8",
                  "Golden hour — backlit, the sun at 10° above the horizon, their hair catching fire.",
                  "Ocean meeting the beach, the sun's path reflected on the water toward camera.",
                  "Both women walking into the shallow water at the shoreline, hands linked, spray catching the golden light around their ankles. Backlit and glowing. This is paradise."),
            scene(SHAY_DESC, {"Angeil": None},
                  "Sony A7 IV", "35mm f/5.6",
                  "Wide, golden hour, the full beach-to-sky panorama.",
                  "The full beach: sand, water, palms, the warm sky going peach and gold.",
                  "Wide enough to see both women as part of the beach, not just on it — small figures in the golden world. They are standing facing each other, both smiling. A private moment in a public paradise."),
        ],
    },

    # DAYS 6-10: Shay + Jazmine
    {
        "id": "private_jet",
        "friends": {"Jazmine": FRIEND_REFS["Jazmine"]},
        "outfit": "OUTFITS_2026/Baby Blue OutFit .png",
        "env": "ENVS/Private Jet Black Table.jpg",
        "caption": "The boarding pass said first class. The energy said private 💅🏾✈️\n\n#shaysofine #jetset #luxurylife #itgirl #travelbae",
        "shots": [
            scene(SHAY_DESC, {"Jazmine": None},
                  "Canon EOS R5", "50mm f/1.4",
                  "Private jet interior — warm recessed lighting overhead, soft and diffused, no harsh shadows.",
                  "Cream leather interior, dark tray tables, champagne flutes on the table between them, city visible through the oval window.",
                  "Shay reclined in the private jet seat, baby blue outfit against dark leather, looking at Jazmine beside her. Jazmine is mid-story, animated, one hand gesturing. Two women living well, talking freely at altitude."),
            scene(SHAY_DESC, {"Jazmine": None},
                  "Canon EOS R5", "85mm f/1.2",
                  "Warm jet interior light — faces perfectly lit from slightly above.",
                  "Champagne flute in the foreground, the oval window showing blue sky.",
                  "Both women looking directly at camera — champagne glasses raised in a toast, matching energy, different beauty. Shay: sleek blonde bob and baby blue. Jazmine: warm brown skin and long natural hair. Together they are the vision."),
            scene(SHAY_DESC, {"Jazmine": None},
                  "Canon EOS R5", "35mm f/2.8",
                  "Slightly wider, the full jet interior visible.",
                  "The full private jet: cream leather, black tables, oval windows, the cloud layer below.",
                  "Shay and Jazmine in their respective seats, both with sunglasses on, looking out the window. Shot from slightly behind and to the side. Luxury and ease at 40,000 feet."),
        ],
    },
    {
        "id": "elephant_adventure",
        "friends": {"Jazmine": FRIEND_REFS["Jazmine"]},
        "outfit": "OUTFITS_2026/Green Christian Dior .jpg",
        "env": "ENVS_2026/Walking With Elephants .png",
        "caption": "Walked with elephants and didn't even flinch 🐘\n\nSoft girl era includes elephant sanctuaries apparently 💅🏾\n\n#elephants #thailand #travelbae #shaysofine #adventuregirl",
        "shots": [
            scene(SHAY_DESC, {"Jazmine": None},
                  "Canon EOS R5", "85mm f/2.0",
                  "Lush Thai jungle light — dappled through the tree canopy, green and warm, soft on their skin.",
                  "Elephant sanctuary in northern Thailand — giant grey elephants among bamboo forest, the lush green jungle stretching in every direction.",
                  "Shay in green Dior, hand gently on the elephant's flank, Jazmine beside her, both watching the animal with genuine wonder. Their expressions soft, not posed. The elephant is enormous and gentle beside them."),
            scene(SHAY_DESC, {"Jazmine": None},
                  "Canon EOS R5", "135mm f/2.8",
                  "Long lens compression — jungle bokeh rich and layered.",
                  "More elephants visible in the background, moving through the bamboo.",
                  "Jazmine has her arm around Shay from behind, both laughing as a baby elephant approaches them. Joy completely unmanufactured. The best frames are the ones you can't plan."),
            scene(SHAY_DESC, {"Jazmine": None},
                  "Canon EOS R5", "35mm f/4",
                  "Wider, the full sanctuary atmosphere.",
                  "Jungle, elephants, guides in the far background, the scale of the sanctuary visible.",
                  "Shay and Jazmine walking together through the sanctuary, a large elephant following them closely behind. Wide enough to see the full scene — two women completely at home in this extraordinary world."),
        ],
    },
    {
        "id": "lakers_game",
        "friends": {"Jazmine": FRIEND_REFS["Jazmine"]},
        "outfit": "OUTFITS_2026/Pink Leaorpatd Track Suit .jpg",
        "env": "ENVS/Lakers Game.jpg",
        "caption": "Courtside and looking like the real MVP 🏀\n\nThey came to watch the game. They ended up watching us.\n\n#lakers #courtside #shaysofine #itgirl #sportsbabe",
        "shots": [
            scene(SHAY_DESC, {"Jazmine": None},
                  "Canon EOS R5", "135mm f/2.0",
                  "Stadium overhead lighting — bright and even, creating clean catchlights. Players and court blurred in background.",
                  "Crypto.com Arena courtside seats — the Lakers court visible, players warming up in soft focus, courtside crowd behind.",
                  "Shay in the pink leopard tracksuit, seated courtside, back slightly turned to show off the fit, blonde bob perfect. Jazmine beside her, leaning over saying something close to her ear. Both mid-genuine moment."),
            scene(SHAY_DESC, {"Jazmine": None},
                  "Canon EOS R5", "85mm f/1.8",
                  "Stadium lights creating drama on their faces — rich and directional.",
                  "Court behind them, the arena crowd a blur of color in the background.",
                  "Both standing — Shay with hands raised as a player scores, Jazmine grabbing her arm in excitement. Real sports fan energy, unexpected and gorgeous."),
            scene(SHAY_DESC, {"Jazmine": None},
                  "Canon EOS R5", "50mm f/2.0",
                  "Arena atmosphere — warm and electric.",
                  "Full courtside setup — the court, the benches, the arena.",
                  "Portrait moment during a timeout — both women looking at camera. Shay: cool and confident. Jazmine: bright smile. The fit, the venue, the vibe — all aligned."),
        ],
    },
    {
        "id": "desert_pool",
        "friends": {"Jazmine": FRIEND_REFS["Jazmine"]},
        "outfit": "OUTFITS_INF/SwimSuits/",
        "env": "ENVS/Desert Pool Mirage.jpg",
        "caption": "Desert heat + infinity pool = the only equation that matters 🏜️💦\n\n#poolday #desert #shaysofine #luxurylifestyle #softgirlera",
        "shots": [
            scene(SHAY_DESC, {"Jazmine": None},
                  "Sony A7 IV", "85mm f/1.4",
                  "Desert midday — hard overhead sun, pure white fill from the light stone deck, incredibly sharp catchlights.",
                  "Desert infinity pool overlooking a vast landscape — red rock formations, not another person for miles, pool water a shocking blue against the tan desert.",
                  "Shay at the pool's infinity edge, back to camera, looking out at the desert. Jazmine beside her, one hand trailing in the pool water. The pool's edge appears to drop straight into the desert valley below."),
            scene(SHAY_DESC, {"Jazmine": None},
                  "Sony A7 IV", "50mm f/1.8",
                  "Both half-submerged, water level shooting — the pool horizon and desert beyond at eye level.",
                  "Water surface catching sky reflection, desert rock formations in the background.",
                  "In the pool together — Shay's blonde bob at the water's edge, Jazmine floating on her back. The pool's geometry creating leading lines to the desert behind them."),
            scene(SHAY_DESC, {"Jazmine": None},
                  "Sony A7 IV", "28mm f/5.6",
                  "Wide — the full scene, desert to sky.",
                  "Pool, deck, desert panoramic, the sky enormous above.",
                  "Both women on the pool edge, feet in the water, the vast desert landscape behind them. Wide enough to feel the scale and the solitude. Two women in paradise they made for themselves."),
        ],
    },
    {
        "id": "podcast_studio",
        "friends": {"Jazmine": FRIEND_REFS["Jazmine"]},
        "outfit": "OUTFITS_2026/Gray Biker firl fit .jpg",
        "env": "ENVS/Podcast Studio .jpg",
        "caption": "New chapter unlocked 🎙️\n\nBuilding something that speaks for itself. With someone who gets it.\n\n#podcast #shaysofine #girlboss #aiinfluencer #softgirlera",
        "shots": [
            scene(SHAY_DESC, {"Jazmine": None},
                  "Canon EOS R5", "50mm f/1.8",
                  "Podcast studio — neon signs casting colored light, soft overhead fill, no harshness. Intimate and creative.",
                  "Podcast studio: boom arms, microphones, sound foam panels, neon sign glowing on the back wall, recording equipment blinking.",
                  "Shay seated at the mic in gray biker fit, leaning forward engaged. Jazmine across from her, headphones on, making a point. Both completely in the creative zone."),
            scene(SHAY_DESC, {"Jazmine": None},
                  "Canon EOS R5", "85mm f/1.4",
                  "Close — faces lit by neon and overhead, all the complexity of the studio in the background.",
                  "Microphones close in the foreground, sound foam behind, recording light on.",
                  "Shay mid-laugh at what Jazmine just said. Jazmine watching her with satisfaction — the best podcasts are when the host can't contain herself. Real moment, unplanned."),
            scene(SHAY_DESC, {"Jazmine": None},
                  "Canon EOS R5", "28mm f/2.8",
                  "Wide studio — the full creative environment.",
                  "The full studio: both women at the setup, equipment everywhere, the neon glow filling the room.",
                  "Wide establishing — both women visible in their full studio setup, professional and vibrant. The creative space as character."),
        ],
    },

    # DAYS 11-15: Shay + Carli
    {
        "id": "pink_bedroom_glam",
        "friends": {"Carli": FRIEND_REFS["Carli"]},
        "outfit": "OUTFITS_2026/Pink STudent Uniform .png",
        "env": "ENVS/Pink Bedroom Sunset .jpg",
        "caption": "Woke up like this 💕 (took two hours but still)\n\nGirl time hits different.\n\n#morningvibes #shaysofine #softgirlera #pinklife #itgirl",
        "shots": [
            scene(SHAY_DESC, {"Carli": None},
                  "Fujifilm GFX 100S", "63mm f/2.8",
                  "Pink bedroom at sunset — warm peach and rose light streaming through sheer curtains, the most flattering light imaginable. Pure femininity in the photons.",
                  "Pastel pink bedroom: silk sheets, flower arrangements, a vanity mirror with bulbs glowing, the sunset visible through gauze curtains.",
                  "Shay on the bed in pink student uniform fit, legs crossed, looking at Carli who is getting ready at the vanity. Carli half-turned, mid-swipe of lip gloss. A real getting-ready moment."),
            scene(SHAY_DESC, {"Carli": None},
                  "Fujifilm GFX 100S", "110mm f/2.0",
                  "Sunset peach light — the most flattering possible, skin tones rich and warm.",
                  "Bed close up, the pink room details.",
                  "Both women on the bed, legs across each other's laps, phones down, in actual conversation. The kind of moment that only happens when you're with your real girl. Warm, intimate, real."),
            scene(SHAY_DESC, {"Carli": None},
                  "Fujifilm GFX 100S", "45mm f/3.5",
                  "Wider — the full pink bedroom visible.",
                  "The full pink bedroom at sunset: vanity, bed, flowers, the warm light everywhere.",
                  "Shay standing, Carli on the bed behind her, both ready and glowing. The pink room creating a frame around them both. Ready for wherever the night takes them."),
        ],
    },
    {
        "id": "horse_riding",
        "friends": {"Carli": FRIEND_REFS["Carli"]},
        "outfit": "OUTFITS_2026/White  SHort Jogiing SUit .jpg",
        "env": "ENVS_2026/Horse Riding Through Water .jpg",
        "caption": "She rides horses through water like it is a casual Tuesday 🐴💦\n\nWith her girl. Obviously.\n\n#horseriding #shaysofine #travelbae #adventuregirl #softgirlera",
        "shots": [
            scene(SHAY_DESC, {"Carli": None},
                  "Canon EOS R5", "135mm f/2.8",
                  "Hard Caribbean midday light — the water beneath the horses' hooves catching the sun in a thousand directions.",
                  "Shallow tropical water — crystal clear over white sand, the horses moving through it, spray catching the sun.",
                  "Shay on horseback, back to camera in white jogging suit, the horse moving through the shallow water. Carli on her own horse beside her, hair blowing, laughing. The spray around the hooves catching sunlight like diamonds."),
            scene(SHAY_DESC, {"Carli": None},
                  "Canon EOS R5", "85mm f/2.0",
                  "Tracking shot — motion implied, horses in stride.",
                  "Water, sky, the Caribbean landscape.",
                  "Both looking at each other mid-ride — Shay over her shoulder at Carli, both with the biggest smiles. The horses in step. Adventure and friendship and beauty all at once."),
            scene(SHAY_DESC, {"Carli": None},
                  "Canon EOS R5", "35mm f/5.6",
                  "Wide — full water, full sky, horses small in the frame.",
                  "The full Caribbean seascape with horses — epic and free.",
                  "Wide enough to show both women on horseback from a distance, the water stretching in every direction, the blue sky above. Two women as small beautiful points in a vast paradise."),
        ],
    },
    {
        "id": "matching_set_dior",
        "friends": {"Carli": FRIEND_REFS["Carli"]},
        "outfit": "OUTFITS_INF/Matching Sets/Christian Rainbow dior Set.jpg",
        "env": "ENVS/Colorfol Lounge Room .jpg",
        "caption": "Christian Dior for the regular Tuesday 🌈\n\nBecause why not?\n\n#dior #matchingset #shaysofine #itgirl #luxuryfashion",
        "shots": [
            scene(SHAY_DESC, {"Carli": None},
                  "Hasselblad X2D", "80mm f/2.8",
                  "Colorful lounge — warm overhead lighting, the vibrant room colors themselves acting as fill. Rich, saturated, luxurious.",
                  "High-end colorful lounge: jewel-tone sofas, art on the walls, flowers in oversized vases. Every surface curated.",
                  "Shay standing in the rainbow Dior set, hand on hip, looking at Carli beside her who is examining one of Shay's bracelets. The colors of the room matching and clashing with the Dior in the most intentional way."),
            scene(SHAY_DESC, {"Carli": None},
                  "Hasselblad X2D", "110mm f/2.0",
                  "Tight and beautiful — both faces in the warm lounge light.",
                  "The lounge colors blurring behind them in medium-format bokeh.",
                  "Both women facing camera — Shay in the rainbow Dior, Carli in her own look. Two women, two aesthetics, one shared energy. Direct eye contact. Confident."),
            scene(SHAY_DESC, {"Carli": None},
                  "Hasselblad X2D", "45mm f/4",
                  "Wider — the full lounge scene.",
                  "The full lounge: all the color, all the texture, the full art-filled space.",
                  "Shay and Carli on the sofa, posed but not stiff — legs crossed, drinks on the side table, conversation paused for the camera. The room a masterpiece around them."),
        ],
    },
    {
        "id": "night_out_red",
        "friends": {"Carli": FRIEND_REFS["Carli"]},
        "outfit": "OUTFITS_INF/NightOut /Leather Red BodySuit .jpg",
        "env": "ENVS/Beach Front Restaurant .jpg",
        "caption": "Red is not a color. It is a warning 🔴\n\nProceed accordingly.\n\n#shaysofine #nightout #redoutfit #itgirl #softgirlera",
        "shots": [
            scene(SHAY_DESC, {"Carli": None},
                  "Sony A7R V", "85mm f/1.4",
                  "Beachfront restaurant at night — warm string lights and candlelight, the ocean darkness behind. The most flattering available light.",
                  "Beachfront restaurant: string lights overhead, ocean in the background, other dining guests in soft bokeh, flickering candles on the tables.",
                  "Shay in the red leather bodysuit, back to camera, the bodysuit glowing in the warm light. Carli facing her across the table, looking up at her with an approving smile. The whole restaurant is her runway."),
            scene(SHAY_DESC, {"Carli": None},
                  "Sony A7R V", "50mm f/1.4",
                  "Candlelight — intimate, warm, zero flash. The shadows doing half the work.",
                  "The table: wine glasses, a small candle, the ocean behind.",
                  "Both women seated at the table, Shay leaning forward on her elbows, the red leather bodysuit visible. Carli across from her, wine glass in hand, both in conversation. The energy: two women who own every room they enter."),
            scene(SHAY_DESC, {"Carli": None},
                  "Sony A7R V", "35mm f/2.0",
                  "Slightly wider, the full restaurant atmosphere.",
                  "The beachfront restaurant's full breadth — string lights, ocean, candlelit tables, other guests.",
                  "Shay standing, Carli seated — Shay's red bodysuit in the foreground, the restaurant and ocean stretching behind. She is the red in this painting."),
        ],
    },
    {
        "id": "waterfall_cave",
        "friends": {"Carli": FRIEND_REFS["Carli"]},
        "outfit": "OUTFITS_INF/SwimSuits/",
        "env": "ENVS/Waterfall Cave Tub.jpg",
        "caption": "Found ourselves in a waterfall cave and honestly did not want to leave 🌊\n\n#waterfall #nature #shaysofine #travelbae #adventure",
        "shots": [
            scene(SHAY_DESC, {"Carli": None},
                  "Canon EOS R5", "35mm f/2.8",
                  "Cave light — diffused through the canopy and waterfall mist, soft and magical. No harsh shadows. The whole scene glows.",
                  "Dramatic cave waterfall — cascading water catching the diffused jungle light, lush tropical vegetation at every edge, a natural pool beneath.",
                  "Shay and Carli in the natural cave pool, both looking up at the waterfall above them. The mist in the air catching the light. The scale of the cave behind them enormous and beautiful."),
            scene(SHAY_DESC, {"Carli": None},
                  "Canon EOS R5", "85mm f/2.0",
                  "Waterfall mist light — dewy and glowing.",
                  "Water, vegetation, the cave walls.",
                  "Carli has her head back, eyes closed, the waterfall mist on her skin. Shay is watching her with a quiet smile. Peace found together."),
            scene(SHAY_DESC, {"Carli": None},
                  "Canon EOS R5", "24mm f/4",
                  "Wide — the full cave, full waterfall, both women small in the frame.",
                  "The cave's full drama — the fall, the pool, the jungle, the light coming through.",
                  "Wide enough to show the cave's full scale with both women in the pool. The waterfall towers behind them. They are impossibly small and impossibly beautiful in this wild place."),
        ],
    },

    # DAYS 16-20: Shay + 2 friends (Angeil + Destiny)
    {
        "id": "jamaica_river",
        "friends": {"Angeil": FRIEND_REFS["Angeil"], "Destiny": FRIEND_REFS["Destiny"]},
        "outfit": "OUTFITS_2026/Jamaicanshorts .jpg",
        "env": "ENVS_2026/River Ride Jamaica .jpg",
        "caption": "Jamaica river ride was NOT on the itinerary 🌿\n\nBut the girls were, and that made it perfect.\n\n#jamaica #caribbean #travelbae #shaysofine",
        "shots": [
            scene(SHAY_DESC, {"Angeil": None, "Destiny": None},
                  "Fujifilm X-T5", "23mm f/2.0",
                  "Lush Jamaica — green-gold light filtered through jungle canopy, dappled on the water surface.",
                  "Bamboo raft on a Jamaican river — lush green banks both sides, hanging vines, the water jade-green and clear.",
                  "Three women on a bamboo raft — Shay front center, Angeil to her left, Destiny to her right. All in Jamaica shorts. The river guide visible behind them. Three women, one raft, pure joy."),
            scene(SHAY_DESC, {"Angeil": None, "Destiny": None},
                  "Fujifilm X-T5", "56mm f/1.4",
                  "River light — green and warm, filtered through tropical canopy.",
                  "The river, the jungle banks, another raft in the far distance.",
                  "Candid mid-raft — all three laughing, Angeil pointing at something in the river, Destiny holding Shay's arm. The kind of trip they'll talk about for years."),
            scene(SHAY_DESC, {"Angeil": None, "Destiny": None},
                  "Fujifilm X-T5", "16mm f/4",
                  "Wide — the full river, the full jungle, the raft small in the lush scene.",
                  "Jamaica river in full — the bamboo raft, the green banks, the sky framed by jungle.",
                  "Wide shot of all three women on the raft, arms spread, leaning out over the water. The jungle magnificent around them. Three queens on a river in paradise."),
        ],
    },
    {
        "id": "van_cleef_set",
        "friends": {"Angeil": FRIEND_REFS["Angeil"], "Destiny": FRIEND_REFS["Destiny"]},
        "outfit": "OUTFITS_INF/Matching Sets/VanCleef Set rainbow .jpg",
        "env": "ENVS/Flower Leopard room .jpg",
        "caption": "Van Cleef on a Monday because the week needed a reason 💎\n\n#vancleef #luxury #shaysofine #matchingset #itgirl",
        "shots": [
            scene(SHAY_DESC, {"Angeil": None, "Destiny": None},
                  "Hasselblad X2D", "80mm f/2.8",
                  "Flower-leopard room — the most maximalist space imaginable, warm and soft light throughout.",
                  "Flower-leopard print room: every surface a pattern, flowers real and in wallpaper, leopard print furniture, the opulence almost comical and completely iconic.",
                  "Three women in the room — Shay in the Van Cleef rainbow set, Angeil and Destiny in their own luxurious looks. Triangle arrangement: Shay slightly forward, the other two flanking. All three looking at camera with quiet authority."),
            scene(SHAY_DESC, {"Angeil": None, "Destiny": None},
                  "Hasselblad X2D", "110mm f/2.0",
                  "Close — faces in the maximalist warm light.",
                  "The room's patterns blurring behind them.",
                  "Shay and Angeil facing each other, Destiny just visible at the edge — they are mid-conversation, Van Cleef jewelry catching the light on Shay's wrist. The energy of three women who know their worth."),
            scene(SHAY_DESC, {"Angeil": None, "Destiny": None},
                  "Hasselblad X2D", "45mm f/4",
                  "The full room — maximum context, maximum opulence.",
                  "Every inch of the flower-leopard room visible.",
                  "Wide — all three women arranged in the room, the maximalist setting framing them perfectly. The room is almost too much. They are exactly enough."),
        ],
    },
    {
        "id": "atl_airport",
        "friends": {"Angeil": FRIEND_REFS["Angeil"], "Destiny": FRIEND_REFS["Destiny"]},
        "outfit": "OUTFITS_2026/Orange SHerbert Tracksuit.jpg",
        "env": "ENVS_2026/Welcome to Atlanta Airport .jpg",
        "caption": "ATL to everywhere 🛫\n\nHartsfield serving as our runway per usual.\n\n#atlanta #airport #shaysofine #travelbae #itgirl",
        "shots": [
            scene(SHAY_DESC, {"Angeil": None, "Destiny": None},
                  "Leica Q3", "28mm f/2.0",
                  "Airport terminal — bright overhead fluorescent but also large skylights creating patches of natural light. Energetic.",
                  "Hartsfield-Jackson — moving walkway, gate signs, other travelers blurred past.",
                  "Three women walking the terminal in a line, Shay in the orange sherbet tracksuit leading, Angeil and Destiny matching her stride. Everyone else blurred in motion around them. They are still. Sharp. Moving with purpose."),
            scene(SHAY_DESC, {"Angeil": None, "Destiny": None},
                  "Leica Q3", "50mm f/2.0",
                  "Three-quarter, natural terminal light.",
                  "Gate seating, departure boards, the airport's constant motion.",
                  "All three women at the gate, sitting together — Shay and Angeil on one row, Destiny on the armrest. Bags between them, all three in sunglasses. The pre-flight moment: excited, stylish, ready."),
            scene(SHAY_DESC, {"Angeil": None, "Destiny": None},
                  "Leica Q3", "35mm f/4",
                  "Wider — the airport scale visible around them.",
                  "The full ATL terminal — vaulted ceilings, light, the organized chaos of a major hub.",
                  "Wide — three women small in the enormous terminal, mid-stride. The architecture of the airport as their backdrop. The world their destination."),
        ],
    },
    {
        "id": "pink_petal_bath",
        "friends": {"Angeil": FRIEND_REFS["Angeil"], "Carli": FRIEND_REFS["Carli"]},
        "outfit": "OUTFITS_2026/White Christian Dior .jpg",
        "env": "ENVS/Pink Pedals Bath .jpg",
        "caption": "She draws her own bath and fills it with flowers 🌸\n\nThis is the soft life.\n\n#softgirlera #selfcare #shaysofine #luxurylife #pinklife",
        "shots": [
            scene(SHAY_DESC, {"Angeil": None, "Carli": None},
                  "Canon EOS R5", "85mm f/1.2",
                  "Pink petal bath — soft afternoon light through frosted glass, the rose petals scattering the light in warm tones.",
                  "A deep soaking tub filled with rose petals, surrounded by candles and flowers. The bathroom all pink marble and gold fixtures.",
                  "Shay at the bath edge in white Dior, one hand trailing in the petal-filled water. Angeil sitting behind her on a toweled surface. Carli standing at the mirror in the background, all three in different moments of self-care. The scene a painting."),
            scene(SHAY_DESC, {"Angeil": None, "Carli": None},
                  "Canon EOS R5", "50mm f/1.4",
                  "Soft pink light — the petals and candles creating the warmest possible ambience.",
                  "The bath, the petals, the candles.",
                  "Shay and Angeil facing each other over the petal bath, Carli visible behind them. Three women in a moment of luxurious stillness. Rose petals floating between them."),
            scene(SHAY_DESC, {"Angeil": None, "Carli": None},
                  "Canon EOS R5", "35mm f/2.8",
                  "Wider — the full beautiful bathroom.",
                  "The full pink marble bathroom, all three women, candles and petals everywhere.",
                  "Wide — all three women in different poses around the bath. The scene is maximally feminine and completely deliberate. Luxury as a self-given right."),
        ],
    },
    {
        "id": "braves_game",
        "friends": {"Jazmine": FRIEND_REFS["Jazmine"], "Carli": FRIEND_REFS["Carli"]},
        "outfit": "OUTFITS_2026/Blue Jean Skirt FIt .jpg",
        "env": "ENVS_2026/Atlanta Braves Game .jpg",
        "caption": "Atlanta Braves game but the real highlight was the fit 😌⚾\n\n#atlantabraves #baseball #shaysofine #itgirl #sportsbae",
        "shots": [
            scene(SHAY_DESC, {"Jazmine": None, "Carli": None},
                  "Canon EOS R5", "135mm f/2.0",
                  "Stadium lights at dusk — that magic hour when the stadium lights are on but the sky is still blue and warm. Perfect.",
                  "Truist Park — the baseball diamond behind them, stadium lights blazing, crowd in the background, the Atlanta skyline visible.",
                  "Three women in their stadium seats — Shay in the blue jean skirt fit, Jazmine and Carli flanking her. All three watching the game, then one of them says something and all three burst out laughing. Caught mid-laugh by the camera."),
            scene(SHAY_DESC, {"Jazmine": None, "Carli": None},
                  "Canon EOS R5", "85mm f/1.8",
                  "Stadium dusk light — blue sky, warm stadium lights, perfect blend.",
                  "Stadium crowd blurred behind them.",
                  "Three-quarter — Shay standing, the other two seated beside her, all three looking at camera. Shay has her hand up ready to cheer. The fit doing exactly what it was meant to."),
            scene(SHAY_DESC, {"Jazmine": None, "Carli": None},
                  "Canon EOS R5", "50mm f/2.0",
                  "Stadium atmosphere — the game happening.",
                  "The full stadium context.",
                  "Wide — all three women visible, the game and stadium as backdrop. Three friends at a baseball game in Atlanta, impossibly stylish, having the best time."),
        ],
    },

    # DAYS 21-25: Shay + Sophia
    {
        "id": "dior_green_editorial",
        "friends": {"Sophia": FRIEND_REFS["Sophia"]},
        "outfit": "OUTFITS_2026/Green Christian Dior .jpg",
        "env": "ENVS/Almafi Coast 1.jpg",
        "caption": "Green Dior because she said so 💚\n\nNo further explanation needed.\n\n#greendior #shaysofine #highfashion #itgirl #luxuryfashion",
        "shots": [
            scene(SHAY_DESC, {"Sophia": None},
                  "Hasselblad X2D", "80mm f/2.8",
                  "Amalfi morning — that Mediterranean light that exists only between 8 and 10am, golden and clean and perfect.",
                  "Amalfi Coast terrace — colorful buildings cascading below, the blue sea stretching to the horizon, a pergola with bougainvillea overhead.",
                  "Shay in the green Dior against the white terrace wall, Sophia beside her in her own elevated look. The complementary aesthetics: Shay's melanin and blonde bob, Sophia's light skin and warm features. Both stunning in opposite ways."),
            scene(SHAY_DESC, {"Sophia": None},
                  "Hasselblad X2D", "110mm f/2.0",
                  "Italian morning light — directional, golden, precise.",
                  "The sea and cliffs in soft medium-format bokeh behind them.",
                  "Both women facing camera — Shay's green Dior, Sophia in white. The Amalfi coast in the background. Fashion campaign energy, two women, two worlds, one frame."),
            scene(SHAY_DESC, {"Sophia": None},
                  "Hasselblad X2D", "45mm f/4",
                  "Wide — the full Amalfi panorama.",
                  "The coast in full: villages, sea, sky.",
                  "Wide — both women small against the enormous beautiful coast. They look at each other and laugh. The location is a masterpiece. So are they."),
        ],
    },
    {
        "id": "night_out_animal",
        "friends": {"Sophia": FRIEND_REFS["Sophia"]},
        "outfit": "OUTFITS_INF/NightOut /Animal Print FLoor red Floor length .jpg",
        "env": "ENVS/Beach Front Restaurant .jpg",
        "caption": "Animal print never left. She just brought it back 🐆\n\n#animalprintfit #shaysofine #nightout #itgirl #fashiongirl",
        "shots": [
            scene(SHAY_DESC, {"Sophia": None},
                  "Sony A7R V", "85mm f/1.4",
                  "Glamorous venue — warm string lights, candlelight, all available, no flash. The most cinematic evening light.",
                  "Upscale beachfront venue at night — string lights, the ocean darkness behind, other well-dressed guests blurred.",
                  "Shay in the floor-length animal print dress, standing. Sophia beside her in an equally elevated look. The dress commands the room. Shay doesn't move to let it — she moves and it follows her."),
            scene(SHAY_DESC, {"Sophia": None},
                  "Sony A7R V", "50mm f/1.4",
                  "Candlelight — intimate, warm, perfect.",
                  "Table, candles, ocean behind.",
                  "Both women seated, Shay's animal print fabric pooling around her. Their wine glasses catching the candlelight. A private moment of ease between two women at a beautiful table."),
            scene(SHAY_DESC, {"Sophia": None},
                  "Sony A7R V", "35mm f/2.0",
                  "Slightly wider — the venue atmosphere.",
                  "The full beachfront restaurant with ocean behind.",
                  "Shay walking ahead of Sophia into the venue, the animal print dress in full motion. Sophia following, laughing. The dress's long hem catching the light."),
        ],
    },
    {
        "id": "vacay_bedroom_morning",
        "friends": {"Sophia": FRIEND_REFS["Sophia"]},
        "outfit": "OUTFITS_2026/White Tube Bodysuit .jpg",
        "env": "ENVS_2026/Vacay Bedroom .jpg",
        "caption": "Vacay bedroom mornings hit different 🌅\n\nWhen there is nowhere to be and good company to have it with.\n\n#vacaymode #shaysofine #softgirlera #morningvibes #luxurytravel",
        "shots": [
            scene(SHAY_DESC, {"Sophia": None},
                  "Canon EOS R5", "50mm f/1.4",
                  "Vacation bedroom morning — warm sunrise light through sheer curtains, the most gentle possible light. Honey-warm and soft.",
                  "Beautiful vacation bedroom — unmade white linen, sheer curtains billowing from an open balcony door, the blue sky and sea visible beyond.",
                  "Shay in the white tube bodysuit sitting on the edge of the bed, holding a coffee mug in both hands. Sophia is cross-legged on the bed behind her, both in the slow peace of a vacation morning."),
            scene(SHAY_DESC, {"Sophia": None},
                  "Canon EOS R5", "85mm f/1.2",
                  "Morning light through sheer curtains — the most ethereal soft light.",
                  "Bed, sheer curtains, the balcony beyond.",
                  "Both women standing at the open balcony door, looking out at the view. The curtains billowing around them. The morning too beautiful not to absorb."),
            scene(SHAY_DESC, {"Sophia": None},
                  "Canon EOS R5", "28mm f/2.8",
                  "Wide — the full vacation bedroom visible.",
                  "The whole room: bed, curtains, balcony, view.",
                  "Wide — both women in the full context of the vacation bedroom, the sea visible through the balcony behind them. The best mornings are the slow ones."),
        ],
    },
    {
        "id": "body_suit_yellow",
        "friends": {"Sophia": FRIEND_REFS["Sophia"]},
        "outfit": "OUTFITS_2026/Bodyshorts Yellow.jpg",
        "env": "ENVS/Beach Vibes Tropics.jpg",
        "caption": "Yellow was scared until she showed up 💛\n\n#yellowfit #shaysofine #bodysuit #softgirlera #itgirl",
        "shots": [
            scene(SHAY_DESC, {"Sophia": None},
                  "Canon EOS R5", "85mm f/1.4",
                  "Tropical beach — noon sun, hard overhead, sand filling shadow from below. The yellow outfit blazing.",
                  "Tropical beach: turquoise water, white sand, palm trees, the works.",
                  "Shay in the yellow bodysuit on the tropical beach, Sophia in a complementary look beside her. The yellow against Shay's brown skin against the turquoise water — three perfect colors. Both women looking at each other mid-conversation."),
            scene(SHAY_DESC, {"Sophia": None},
                  "Canon EOS R5", "50mm f/1.8",
                  "Tropical afternoon — the sun moved, now at 45°, warm sidelight.",
                  "Palm trees, ocean, warm sand.",
                  "Both women in the ocean shallows, the water around their ankles, arms around each other's shoulders. Looking at camera, smiling. The tropical sun on their backs."),
            scene(SHAY_DESC, {"Sophia": None},
                  "Canon EOS R5", "35mm f/5.6",
                  "Wide — the full tropical scene.",
                  "The beach, the palms, the sea, the sky.",
                  "Wide — both women small against the enormous tropical panoramic. The yellow bodysuit a perfect punctuation mark in the landscape."),
        ],
    },
    {
        "id": "bathroom_selfie_glam",
        "friends": {"Sophia": FRIEND_REFS["Sophia"]},
        "outfit": "OUTFITS_2026/Blue and WHite BodySUit OFf White .jpg",
        "env": "ENVS_2026/Bathroom Selfie .jpg",
        "caption": "Bathroom mirror said you look good today 💅🏾\n\nI said I know. She said same.\n\n#bathroomselfie #shaysofine #glowup #softgirlera #itgirl",
        "shots": [
            scene(SHAY_DESC, {"Sophia": None},
                  "iPhone 15 Pro aesthetic on Canon EOS R5", "35mm f/2.0",
                  "Bathroom mirror light — LED vanity strips creating even clean light on both faces.",
                  "Beautiful white marble bathroom, large illuminated mirror, products artfully arranged on the counter.",
                  "Shay and Sophia doing a mirror selfie together — Shay in the blue and white bodysuit, phone in hand, both looking at the phone's camera in the mirror. Mid-laugh at themselves. Authentic bathroom energy."),
            scene(SHAY_DESC, {"Sophia": None},
                  "Canon EOS R5", "85mm f/1.4",
                  "Bathroom vanity light — clean and flattering.",
                  "Mirror, marble counter, the products.",
                  "Three-quarter — Shay at the mirror applying something, Sophia leaning against the wall watching. Natural, unhurried. The daily ritual made aesthetic."),
            scene(SHAY_DESC, {"Sophia": None},
                  "Canon EOS R5", "50mm f/2.0",
                  "Wider bathroom shot.",
                  "The full marble bathroom.",
                  "Both women in the full bathroom context — Shay and Sophia ready to leave but one more look in the mirror. They look good. They know it."),
        ],
    },

    # DAYS 26-30: Shay + 3-4 friends (group energy)
    {
        "id": "rich_girl_set",
        "friends": {"Angeil": FRIEND_REFS["Angeil"], "Jazmine": FRIEND_REFS["Jazmine"], "Frannie": FRIEND_REFS["Frannie"]},
        "outfit": "OUTFITS_INF/Matching Sets/Rich Girl Set.jpg",
        "env": "ENVS/Colorfol Lounge Room .jpg",
        "caption": "Rich girl set for the rich girl mindset 💰\n\nFour women who built it themselves.\n\n#richgirl #shaysofine #luxuryfashion #matchingset #itgirl",
        "shots": [
            scene(SHAY_DESC, {"Angeil": None, "Jazmine": None, "Frannie": None},
                  "Canon EOS R5", "35mm f/2.8",
                  "Colorful lounge — warm directional lighting, each woman individually lit and visible.",
                  "High-end colorful lounge: jewel tones, flowers, art. The space can handle four women.",
                  "Four women in the lounge — Shay in the Rich Girl set, Angeil, Jazmine, and Frannie in their own elevated looks. Natural grouping: two on the sofa, two standing. Everyone at ease and looking incredible."),
            scene(SHAY_DESC, {"Angeil": None, "Jazmine": None, "Frannie": None},
                  "Canon EOS R5", "85mm f/2.0",
                  "Warmer, tighter — the group chemistry.",
                  "The lounge colors behind them.",
                  "All four women looking at camera — different heights, different skin tones, different hair. Four kinds of beauty, one shared energy. The kind of group that changes the temperature of a room."),
            scene(SHAY_DESC, {"Angeil": None, "Jazmine": None, "Frannie": None},
                  "Canon EOS R5", "24mm f/3.5",
                  "Wide — the full group in the full lounge.",
                  "The complete lounge scene — all four women, all the room.",
                  "Wide — four women, one room, zero wasted space. Every angle is composition. The energy is collective and undeniable."),
        ],
    },
    {
        "id": "fur_boots_winter",
        "friends": {"Angeil": FRIEND_REFS["Angeil"], "Carli": FRIEND_REFS["Carli"]},
        "outfit": "OUTFITS_2026/boots and boyshorts fur .png",
        "env": "ENVS/Pink Bedroom Sunset .jpg",
        "caption": "Winter had no idea what was coming 🤍\n\n#winterfit #shaysofine #furboots #itgirl #softgirlera",
        "shots": [
            scene(SHAY_DESC, {"Angeil": None, "Carli": None},
                  "Fujifilm GFX 100S", "63mm f/2.8",
                  "Pink sunset bedroom — the warmest possible light, peach and gold, absolutely no harsh shadows.",
                  "Pink sunset bedroom: the same space but this time three women and their energy fills it differently.",
                  "Shay in fur boots and boyshorts at the room's center, Angeil on the bed in the background, Carli closer and examining the boots. All three in a moment of genuine playfulness."),
            scene(SHAY_DESC, {"Angeil": None, "Carli": None},
                  "Fujifilm GFX 100S", "110mm f/2.0",
                  "Tight — three faces in the pink light.",
                  "Bedroom in soft focus behind.",
                  "All three women together on the bed, Shay's boots in frame, all three laughing. The fur boots are the joke and the accessory simultaneously."),
            scene(SHAY_DESC, {"Angeil": None, "Carli": None},
                  "Fujifilm GFX 100S", "45mm f/3.5",
                  "Wider — the full pink bedroom.",
                  "The complete pink bedroom scene.",
                  "Wide — three women in the pink sunset bedroom, each in their own moment. Shay standing, Angeil on the bed, Carli at the vanity. A real afternoon with real women who are real friends."),
        ],
    },
    {
        "id": "soft_girl_lounge",
        "friends": {"Jazmine": FRIEND_REFS["Jazmine"], "Kayla": FRIEND_REFS["Kayla"]},
        "outfit": "OUTFITS_2026/Pink Leaorpatd Track Suit .jpg",
        "env": "ENVS/Flower Leopard room .jpg",
        "caption": "Soft girl era is not a phase. It is the final form 💕\n\n#softgirlera #shaysofine #lounge #selfcare #itgirl",
        "shots": [
            scene(SHAY_DESC, {"Jazmine": None, "Kayla": None},
                  "Canon EOS R5", "50mm f/1.8",
                  "Flower-leopard room — maximalist warm light, everywhere you look there is pattern and color.",
                  "The flower-leopard room at its most chaotic-beautiful.",
                  "Three women lounging — Shay in the pink leopard tracksuit on the floor leaning against the sofa, Jazmine draped on the sofa above, Kayla sitting on the arm. Completely at ease. The room is them and they are the room."),
            scene(SHAY_DESC, {"Jazmine": None, "Kayla": None},
                  "Canon EOS R5", "85mm f/1.4",
                  "Tighter — the three of them, the room patterns blurring.",
                  "Flowers and leopard print in bokeh.",
                  "All three looking at camera — Shay, Jazmine, Kayla. Three different kinds of soft girl. One collective era."),
            scene(SHAY_DESC, {"Jazmine": None, "Kayla": None},
                  "Canon EOS R5", "28mm f/3.5",
                  "Wide — the full maximalist scene.",
                  "Every inch of the flower-leopard room with three women in it.",
                  "Wide — the room, the women, the collective softness. Everything intentional. Nothing accidental."),
        ],
    },
    {
        "id": "brazil_nike_casual",
        "friends": {"Angeil": FRIEND_REFS["Angeil"], "Frannie": FRIEND_REFS["Frannie"], "Saddie": FRIEND_REFS["Saddie"]},
        "outfit": "OUTFITS_2026/Brazil Nikesocks .png",
        "env": "ENVS/Beach Vibes Tropics.jpg",
        "caption": "Brazil energy every day 🇧🇷\n\nThe girls were mandatory.\n\n#brazil #shaysofine #nikestyle #casualfit #itgirl",
        "shots": [
            scene(SHAY_DESC, {"Angeil": None, "Frannie": None, "Saddie": None},
                  "Sony A7 IV", "35mm f/2.0",
                  "Tropical afternoon — warm sun at 45°, lively and bright.",
                  "Tropical beachfront: palm trees, bright blue sky, other beach-goers in the far distance.",
                  "Four women walking the beachfront together — Shay in Brazil Nike socks at the front, Angeil, Frannie, and Saddie behind her in their own casual looks. Walking with that energy that makes people stop and look."),
            scene(SHAY_DESC, {"Angeil": None, "Frannie": None, "Saddie": None},
                  "Sony A7 IV", "85mm f/1.8",
                  "Tropical warm light — all four faces caught.",
                  "Tropical beach behind them.",
                  "All four women at the beach — Shay with her arms around Angeil and Frannie, Saddie on the other side. Four women from different backgrounds, one shared vibe."),
            scene(SHAY_DESC, {"Angeil": None, "Frannie": None, "Saddie": None},
                  "Sony A7 IV", "24mm f/4",
                  "Wide — the full tropical beach, all four women.",
                  "The complete beach scene.",
                  "Wide — four women, one tropical paradise. The squad in full effect."),
        ],
    },
    {
        "id": "neo_shay_collab",
        "friends": {"Angeil": FRIEND_REFS["Angeil"], "Jazmine": FRIEND_REFS["Jazmine"], "Carli": FRIEND_REFS["Carli"]},
        "outfit": "OUTFITS_2026/Green Christian Dior .jpg",
        "env": "ENVS/Colorfol Lounge Room .jpg",
        "caption": "When the girls link up, everything elevates 🎬\n\n#shaysofine #squad #girlpower #vlm #aiinfluencer",
        "shots": [
            scene(SHAY_DESC, {"Angeil": None, "Jazmine": None, "Carli": None},
                  "Hasselblad X2D", "80mm f/2.8",
                  "Creative studio / lounge — the best kind of light: directional, warm, complex.",
                  "Modern creative studio turned lounge — screens, comfortable seating, the energy of a place where things get made.",
                  "Four women in the creative space — Shay in green Dior, Angeil, Jazmine, and Carli in their own looks. Not posed for a brand. Just four creative women in a room together."),
            scene(SHAY_DESC, {"Angeil": None, "Jazmine": None, "Carli": None},
                  "Hasselblad X2D", "110mm f/2.0",
                  "Tight, warm, all four faces.",
                  "The studio behind them in beautiful medium-format bokeh.",
                  "All four looking at camera. Four women. Four aesthetics. One vision. The group shot that says everything without saying a word."),
            scene(SHAY_DESC, {"Angeil": None, "Jazmine": None, "Carli": None},
                  "Hasselblad X2D", "45mm f/4",
                  "Wide — the full studio scene, four women.",
                  "The complete creative space.",
                  "Wide — four women in a creative space, looking like they run it. Because they do."),
        ],
    },
]


def resolve(path_str: str) -> str:
    s = str(path_str)
    s = s.replace("OUTFITS_2026/", str(OUTFITS_2026) + "/")
    s = s.replace("OUTFITS_INF/", str(OUTFITS_INF) + "/")
    s = s.replace("ENVS_2026/", str(ENVS_2026) + "/")
    s = s.replace("ENVS/", str(ENVS) + "/")
    return s


def build_assets(carousel: dict, carousel_idx: int) -> list:
    assets = [
        {"path": str(SHAY_BACK),  "label": "Main Character: Shay (back)"},
        {"path": str(SHAY_FRONT), "label": "Main Character: Shay (front)"},
    ]
    for name, refs in carousel["friends"].items():
        for i, ref_path in enumerate(refs):
            if os.path.exists(ref_path):
                label = f"Cast: {name}" if i == 0 else f"Cast: {name} (ref {i+1})"
                assets.append({"path": ref_path, "label": label})

    # Rotate through ALL Shay outfits by carousel index
    if SHAY_ALL_OUTFITS:
        outfit = SHAY_ALL_OUTFITS[carousel_idx % len(SHAY_ALL_OUTFITS)]
        assets.append({"path": str(outfit), "label": "Outfit for Main Character"})

    # Pass Angeil an outfit when she's in the scene
    if "Angeil" in carousel.get("friends", {}) and ANGEIL_ALL_OUTFITS:
        offset = len(ANGEIL_ALL_OUTFITS) // 2
        angeil_outfit = ANGEIL_ALL_OUTFITS[(carousel_idx + offset) % len(ANGEIL_ALL_OUTFITS)]
        assets.append({"path": str(angeil_outfit), "label": "Outfit for Angeil"})

    env_path = resolve(carousel.get("env", "")) if carousel.get("env") else ""
    if env_path and os.path.exists(env_path):
        assets.append({"path": env_path, "label": "Scene Location/Vibe"})

    return assets


def main():
    print("🌟 Shay.So.Fine — 30-Day Carousel Generator (MASTER REWRITE)")
    print(f"Output: {OUTPUT}\n")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    total = len(CAROUSELS)

    for i, carousel in enumerate(CAROUSELS):
        cid = carousel["id"]
        friend_names = list(carousel["friends"].keys())
        print(f"\n{'='*60}")
        print(f"[{i+1}/{total}] {cid} | Cast: Shay + {', '.join(friend_names)}")
        print(f"{'='*60}")

        caption_path = OUTPUT / f"{cid}_caption.txt"
        shay_cta = (
            "\n\nThe soft girl era is not a trend. It is the standard, and she set it herself. "
            "Every look curated, every moment captured, every destination earned. "
            "This is what it looks like when the algorithm works for you — not the other way around.\n\n"
            "The AI content engine behind the aesthetic → vlmcreateflow.com ✨\n"
            "Link in bio. DM for brand partnerships."
        )
        caption_path.write_text(carousel["caption"] + shay_cta)

        assets = build_assets(carousel, i)

        for j, prompt_text in enumerate(carousel["shots"]):
            shot_num = j + 1
            out_path = OUTPUT / f"{cid}_shot{shot_num}.jpg"

            if out_path.exists():
                print(f"  [SKIP] shot {shot_num} exists")
                continue

            print(f"  📸 Shot {shot_num}/3...")

            prompt_data = {
                "positive_prompt": prompt_text,
                "aspect_ratio": "4:5",
                "image_size": "4K",
                "assets": assets,
            }

            result = generate_image_from_prompt(prompt_data, output_folder=str(OUTPUT))

            if result.get("status") == "success" and result.get("image_path"):
                src = Path(result["image_path"])
                if src.exists() and src != out_path:
                    shutil.move(str(src), str(out_path))
                print(f"  ✅ {out_path.name}")

                meta = {
                    "carousel_id": cid,
                    "shot_index": j,
                    "cast": ["Shay"] + friend_names,
                    "cast_count": 1 + len(friend_names),
                    "cast_refs": {
                        "Shay": [str(SHAY_BACK), str(SHAY_FRONT)],
                        **{n: carousel["friends"][n] for n in friend_names},
                    },
                    "outfit": carousel.get("outfit", ""),
                    "scene": prompt_text[:200],
                    "prompt_used": prompt_text,
                    "generated_at": datetime.now().isoformat(),
                }
                meta_path = out_path.with_suffix(".meta.json")
                meta_path.write_text(json.dumps(meta, indent=2))
            else:
                print(f"  ❌ Shot {shot_num} failed")

            if j < len(carousel["shots"]) - 1:
                time.sleep(2)

        if i < total - 1:
            time.sleep(4)

    print(f"\n✅ Done. {total} carousels → {OUTPUT}")


if __name__ == "__main__":
    main()
