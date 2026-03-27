"""
Neo — 30-Day Instagram Carousel Batch Generator  (MASTER REWRITE)
Neo is ALWAYS with Shay (his girl) OR 1 other person. No solo shots.
Master-level photography language throughout.
"""
import os, sys, json, time, shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()
from execution.generate_image import generate_image_from_prompt

BASE = Path(__file__).parent.parent

# ── Neo refs ──────────────────────────────────────────────────────────────────
NEO_HERO     = BASE / "assets/AI Content Creators/Friends/Mens Friends/Neo.png"
NEO_OUTFITS  = BASE / "assets/AI Content Creators/Friends/Mens Friends/Neo Outfits/Mens clothing"
NEO_ENVS     = BASE / "assets/AI Content Creators/Friends/Mens Friends/Neo Environments"

# ── Dynamic outfit pool — ALL Neo outfit files ────────────────────────────────
def _collect_outfits(directory: Path) -> list:
    exts = {".jpg", ".jpeg", ".png"}
    return sorted([f for f in directory.rglob("*") if f.suffix.lower() in exts and not f.name.startswith("._")])

NEO_ALL_OUTFITS   = _collect_outfits(NEO_OUTFITS)

# ── Outfit pools for cast members ─────────────────────────────────────────────
SHAY_OUTFITS_DIR  = BASE / "assets/AI Content Creators/2026 Jan CLothing "
SHAY_INF_DIR      = BASE / "assets/AI Content Creators/Influencer CLothing "
def _collect_shay_outfits():
    exts = {".jpg", ".jpeg", ".png"}
    results = []
    for d in [SHAY_OUTFITS_DIR, SHAY_INF_DIR]:
        results += [f for f in d.rglob("*") if f.suffix.lower() in exts
                    and not f.name.startswith("._")
                    and "Jan 2026 Enviroments" not in str(f)]
    return sorted(results)

SHAY_ALL_OUTFITS  = _collect_shay_outfits()

# Outfit pool map by partner name
PARTNER_OUTFIT_POOL = {
    "Shay":   SHAY_ALL_OUTFITS,
}

# ── Shay refs (Neo's girl) ────────────────────────────────────────────────────
SHAY_BACK    = BASE / "assets/AI Content Creators/Shay.So.Fine/SHAY STOCK Photo/Shay blonde bob back.png"
SHAY_FRONT   = BASE / "assets/AI Content Creators/Shay.So.Fine/SHAY STOCK Photo/Shay blonde bob front .png"
SHAY_BUN     = BASE / "assets/AI Content Creators/Shay.So.Fine/SHAY STOCK Photo/Shay High Bun Back.png"

# ── Friend refs ───────────────────────────────────────────────────────────────
FRIENDS_DIR  = BASE / "assets/AI Content Creators/Friends/Black Influencer Models"
WHITE_DIR    = BASE / "assets/AI Content Creators/Friends/White Influencers"
LATINA_DIR   = BASE / "assets/AI Content Creators/Friends/Latina Influencers"
ANGEIL_HERO  = BASE / "assets/AI Content Creators/Friends/Angeil Master /Angeil Hero image/Angeil.png"
ANGEIL_EYES  = FRIENDS_DIR / "AngeilEyes.JPEG"

FRIEND_REFS = {
    "Shay":     [str(SHAY_BACK), str(SHAY_FRONT)],
    "Jazmine":  [str(FRIENDS_DIR / "Jazmine.jpg")],
    "Carli":    [str(FRIENDS_DIR / "Carli.jpg")],
    "Destiny":  [str(FRIENDS_DIR / "East African Rich Girl .jpg")],
    "MixedBabe":[str(FRIENDS_DIR / "Pretty curly long mixed Girl .jpg")],
    "Sophia":   [str(WHITE_DIR / "Sophia 1.png")],
    "Saddie":   [str(WHITE_DIR / "Saddie 1.png")],
    "Frannie":  [str(LATINA_DIR / "Franscesca .jpg")],
    "Kayla":    [str(LATINA_DIR / "Kayla.jpg")],
    "Ashley":   [str(LATINA_DIR / "Ashley.jpg")],
}

# ── Shared environments ───────────────────────────────────────────────────────
ENVS      = BASE / "assets/AI Content Creators/Environments"
ENVS_2026 = BASE / "assets/AI Content Creators/2026 Jan CLothing /Jan 2026 Enviroments"
OUTPUT    = BASE / "output/users/Neo/Instagram"

# ── Character descriptions ────────────────────────────────────────────────────
NEO_DESC = (
    "Light-skin Black man, well-groomed beard, medium-length curly hair, lean and athletic build, "
    "6'1\", magnetic presence — the kind of man who is always dressed with intention and reads a room the moment he enters it. "
    "Creative director energy. Never try-hard. Always intentional."
)

CAST_DESCS = {
    "Shay":     "Beautiful Black woman with a signature shoulder-length blonde bob, melanin-rich brown skin, modelesque proportions, effortlessly stylish. His girl. The energy between them is lived-in and real.",
    "Jazmine":  "Stunning Black woman, warm brown skin, long natural hair, warm smile — confidence and joy in equal measure.",
    "Carli":    "Beautiful Black woman, deep warm complexion, striking features, fashion-forward energy.",
    "Destiny":  "Beautiful East African woman, stunning bone structure, tall and elegant — the kind of presence that photographers orbit.",
    "MixedBabe":"Beautiful mixed woman, curly hair, warm complexion, effortlessly magnetic.",
    "Sophia":   "Beautiful white woman, bright eyes, warm smile, effortlessly chic — the kind of person who makes any space feel elevated.",
    "Saddie":   "Striking white woman, natural beauty, easy confidence — stylish without trying, magnetic without effort.",
    "Frannie":  "Gorgeous Latina woman, dark hair, warm complexion, expressive energy — she lights up every room she walks into.",
    "Kayla":    "Beautiful Latina woman, radiant brown skin, sharp features, effortlessly stylish with an infectious presence.",
    "Ashley":   "Stunning Latina woman, warm tone, dark eyes, creative energy — the kind of person Neo vibes with instantly.",
}


def scene(neo, person_name, camera, lens, light, env_detail, action,
          film="Kodak Portra 800 emulation, warm cast, natural grain, lifted blacks"):
    """Build a master-level 2-person prompt. Neo + one other."""
    person_desc = CAST_DESCS.get(person_name, "beautiful woman, stylish and magnetic.")
    return (
        f"{camera}, {lens}. "
        f"{light} "
        f"CAST (2 people): {NEO_DESC} {person_desc} "
        f"{env_detail} "
        f"{action} "
        f"{film}. Aspect ratio 4:5."
    )


# ── 30 carousels ─────────────────────────────────────────────────────────────
CAROUSELS = [

    # ── DAYS 1-10: Neo + Shay (couple energy) ────────────────────────────────

    {
        "id": "neo_shay_rooftop_golden",
        "partner": "Shay",
        "outfit": "NEO_OUTFITS/Brown Travis outfit.png",
        "env": "NEO_ENVS/neo with his girl.jpg",
        "caption": "Some places hit different when you bring the right one 🌆\n\n#neo #couple #rooftopvibes #vlm #aiinfluencer",
        "shots": [
            scene(NEO_DESC, "Shay",
                  "Canon EOS R5", "85mm f/1.2L wide open at f/1.4",
                  "Rooftop at golden hour — the city skyline catching the last horizontal light, warm orange pooling across concrete and glass.",
                  "Urban rooftop — HVAC units softened by distance, the city a blur of light behind them, a single empty glass on the ledge.",
                  "Neo stands at the railing, looking out at the city — Shay beside him with her hand resting on his chest, her blonde bob catching the backlight. Neither performing for camera. Both just here."),
            scene(NEO_DESC, "Shay",
                  "Canon EOS R5", "50mm f/2.0",
                  "Three-quarter front, warm backlight still washing the scene — soft fill from the ambient city glow.",
                  "The rooftop, the city shimmer behind them, a warm evening haze.",
                  "Neo has his arm low around Shay's waist, both of them looking at each other mid-conversation. His beard catching the golden light. Her bob soft in the breeze. The city doesn't exist right now."),
            scene(NEO_DESC, "Shay",
                  "Canon EOS R5", "35mm f/4.0",
                  "Wide environmental — the full rooftop at dusk, city lights beginning to pop.",
                  "The full city behind them, the rooftop edge, the vast sky turning deep blue.",
                  "Wide — two figures against the city at magic hour. Small in the best way. The scale is the point."),
        ],
    },
    {
        "id": "neo_shay_kitchen_morning",
        "partner": "Shay",
        "outfit": "NEO_OUTFITS/Simple Every Day slides.jpg",
        "env": "ENVS/Shays Kitchen.jpg",
        "caption": "Mornings built for two 🍳\n\nHer playlist. My coffee. That's all.\n\n#morningvibes #neo #couple #domesticbliss #vlm",
        "shots": [
            scene(NEO_DESC, "Shay",
                  "Fujifilm GFX 100S", "63mm f/2.8",
                  "Kitchen morning light — soft diffuse north-facing window light, no harsh shadows, everything clean and warm.",
                  "Modern kitchen: marble counters, open shelving with ceramics, the smell of coffee in the composition.",
                  "Neo at the counter making coffee, back mostly to camera, Shay sitting on the counter beside him eating something. Morning quiet. Domestic and beautiful."),
            scene(NEO_DESC, "Shay",
                  "Fujifilm GFX 100S", "110mm f/2.0",
                  "Tight — both faces, kitchen light, medium-format rendering the skin tones with extraordinary depth.",
                  "The kitchen in gorgeous bokeh behind.",
                  "Neo looking at Shay who is looking at camera — a classic asymmetric moment. He hasn't noticed she's being photographed. She has. The energy between them legible in a single frame."),
            scene(NEO_DESC, "Shay",
                  "Fujifilm GFX 100S", "45mm f/3.5",
                  "Wider — the full kitchen, morning light.",
                  "The complete kitchen context — the space that holds their morning.",
                  "Both in the kitchen, unhurried. Neo leaning against the counter with his coffee. Shay perched on the island. Sunday morning energy in the middle of a Tuesday."),
        ],
    },
    {
        "id": "neo_shay_dubai_desert",
        "partner": "Shay",
        "outfit": "NEO_OUTFITS/Louis Vutton Brown fit .png",
        "env": "ENVS/Dubai Desert.jpg",
        "caption": "Dubai hit the reset button on everything 🏜️\n\nOut here with the only one that matters.\n\n#dubai #desert #neo #couple #luxury",
        "shots": [
            scene(NEO_DESC, "Shay",
                  "Hasselblad X2D", "80mm f/2.8",
                  "Dubai desert at late afternoon — the sun low and red, light raking across the sand dunes in long dramatic shadows.",
                  "Endless sand dunes, the horizon clean, a luxury 4x4 in the far background, heat shimmer at the edges.",
                  "Neo in Louis Vuitton brown, Shay in a complementary desert look — both standing at the crest of a dune, the world falling away behind them. His hand in hers, neither looking at camera."),
            scene(NEO_DESC, "Shay",
                  "Hasselblad X2D", "110mm f/2.0",
                  "The warm desert red light, tight on both faces — medium-format rendering every detail.",
                  "Sand in soft bokeh, the deep desert behind.",
                  "Both facing camera — Neo slightly behind Shay, his hand on her shoulder. The Louis V brown against the sand. Her blonde bob soft in the desert wind. Squinting slightly into the light. Real."),
            scene(NEO_DESC, "Shay",
                  "Hasselblad X2D", "45mm f/4",
                  "Wide — the desert, the dunes, two small figures against it all.",
                  "The full desert landscape, the scale overwhelming.",
                  "Wide — two people in an enormous landscape. The LV brown a perfect color note against the warm ochre dunes. The world is vast. They are in it together."),
        ],
    },
    {
        "id": "neo_shay_car_night",
        "partner": "Shay",
        "outfit": "NEO_OUTFITS/Everyday black and Red .png",
        "env": "NEO_ENVS/inside Neos car counting.jpg",
        "caption": "Night drives, no destination 🌙\n\nJust the city and her.\n\n#nightdrive #neo #couple #citylife #vlm",
        "shots": [
            scene(NEO_DESC, "Shay",
                  "Sony A7 IV", "35mm f/1.8",
                  "Interior car — city lights streaming through the window creating moving painterly bokeh, dashboard glow as fill.",
                  "Inside a clean luxury car: the dashboard lit, city lights outside the windows painting the interior.",
                  "Neo at the wheel, Shay in the passenger seat turned toward him, her hand on the console near his. The city lights make everything cinematic."),
            scene(NEO_DESC, "Shay",
                  "Sony A7 IV", "50mm f/1.4",
                  "From the back seat — a natural documentary angle, city light constantly shifting.",
                  "The headrests, the city in the windshield, the glow.",
                  "Both in profile, the windshield full of city light in front of them. A specific stillness in a moving car. Night drive conversation energy."),
            scene(NEO_DESC, "Shay",
                  "Sony A7 IV", "85mm f/1.4",
                  "Stopped at a red light — steady light, dramatic city color through the window.",
                  "The interior, the red stoplight glow, the city paused outside.",
                  "Neo looking straight ahead at the red light. Shay looking at him. A frame that tells a whole story in a moment."),
        ],
    },
    {
        "id": "neo_shay_tokyo",
        "partner": "Shay",
        "outfit": "NEO_OUTFITS/Rick Owens Fit .jpg",
        "env": "ENVS/Tokyo Streets .jpg",
        "caption": "Tokyo gave us everything we didn't know we needed 🇯🇵\n\nRick Owens in the rain. Her beside me. Undefeated.\n\n#tokyo #japan #neo #couple #rickowens",
        "shots": [
            scene(NEO_DESC, "Shay",
                  "Leica M11", "35mm f/1.4 Summilux",
                  "Tokyo evening in light rain — neon signs creating complex wet reflections on the pavement, warm and cool colors fighting for dominance.",
                  "Shibuya-style crossing with rain-slicked streets, neon kanji everywhere, the city at full sensory overload behind them.",
                  "Neo in Rick Owens, Shay in an editorial Tokyo look — both walking toward camera with an umbrella between them, the neon city blurring behind. The Rick Owens against the Tokyo neon is a perfect contrast."),
            scene(NEO_DESC, "Shay",
                  "Leica M11", "50mm f/2.0 APO-Summicron",
                  "Under awning — out of the rain, the neon from outside making complex reflections on the wet concrete in front of them.",
                  "The Tokyo street scene through the awning, rain at the edges.",
                  "Both sheltering under an awning, Shay looking up at Neo who is watching the rain. The neon colors painting their faces differently — warm on one side, cool on the other."),
            scene(NEO_DESC, "Shay",
                  "Leica M11", "28mm f/2.0",
                  "Wide Tokyo street — the full environment, rain, neon, humanity.",
                  "The complete Tokyo chaos: signs, people in the distance, wet streets, the works.",
                  "Wide — two people in the rain in Tokyo. Neo and Shay small against the city. The Rick Owens drape still sharp. The city overwhelming and beautiful."),
        ],
    },
    {
        "id": "neo_shay_beach_sunrise",
        "partner": "Shay",
        "outfit": "NEO_OUTFITS/green swim shorts .jpg",
        "env": "ENVS/Beach Vibes Tropics.jpg",
        "caption": "Up before the world. Beach before the crowds. Her beside me always 🌅\n\n#sunrise #beach #neo #couple #morningperson",
        "shots": [
            scene(NEO_DESC, "Shay",
                  "Canon EOS R5", "85mm f/1.4",
                  "Beach at sunrise — the first horizontal light, pink and gold, absolutely no crowds, the water glassy.",
                  "Tropical beach at dawn: empty sand, glassy water, the first birds, the colors no one sees because they don't get up.",
                  "Neo in green swim shorts, Shay in a sunrise look, both standing at the water's edge with their feet in the shallows. The sunrise painting everything warm. The most beautiful quiet."),
            scene(NEO_DESC, "Shay",
                  "Canon EOS R5", "50mm f/1.8",
                  "The sunrise glow on both of them — warm, directional, perfect.",
                  "The empty beach, the sunrise colors, the glassy water.",
                  "Both sitting on the sand facing the ocean, shoulder to shoulder. Shay's blonde bob catching the sunrise perfectly. Neo watching the water. Peaceful in the most earned way."),
            scene(NEO_DESC, "Shay",
                  "Canon EOS R5", "24mm f/4",
                  "Wide — the full beach at sunrise, two silhouettes.",
                  "The beach at its most expansive — all that water, all that sky, two people.",
                  "Wide — their silhouettes against the sunrise, the tropical water stretching to the horizon. Two people who got up early for this. Worth every second."),
        ],
    },
    {
        "id": "neo_shay_art_gallery",
        "partner": "Shay",
        "outfit": "NEO_OUTFITS/Brown luis v .png",
        "env": "ENVS/Art Gallery.jpg",
        "caption": "Art day with her hits different than art day alone 🎨\n\nEverything looks better with context.\n\n#artgallery #neo #couple #culturevulture #vlm",
        "shots": [
            scene(NEO_DESC, "Shay",
                  "Canon EOS R5", "50mm f/2.0",
                  "Gallery lighting — clean museum-grade directional lighting on the art, spilling onto them naturally.",
                  "Modern art gallery: white walls, large canvases, polished concrete floors, the kind of space where silence has weight.",
                  "Neo standing in front of a large abstract canvas, Shay beside him with her head slightly tilted — both genuinely looking. The kind of moment that happens when you actually go to art together."),
            scene(NEO_DESC, "Shay",
                  "Canon EOS R5", "85mm f/1.4",
                  "The gallery light on both of them — clean, directional.",
                  "A large colorful canvas behind them in bokeh.",
                  "Both looking at camera — the canvas behind them a burst of color against Neo's brown Luis V and Shay's look. A portrait in a gallery. The art is also them."),
            scene(NEO_DESC, "Shay",
                  "Canon EOS R5", "35mm f/2.8",
                  "Wide — the gallery space, both of them small in it.",
                  "The full gallery corridor — canvases stretching into the distance, gallery lighting in rows.",
                  "Wide — Neo and Shay walking the gallery together, not posing, just moving from piece to piece. The gallery doing what galleries should do."),
        ],
    },
    {
        "id": "neo_shay_penthouse",
        "partner": "Shay",
        "outfit": "NEO_OUTFITS/burgundy outfit .png",
        "env": "ENVS/Penthouse View .jpg",
        "caption": "Penthouse perspective makes everything clearer 🏙️\n\nHer. The view. The stillness.\n\n#penthouse #neo #couple #luxury #cityview",
        "shots": [
            scene(NEO_DESC, "Shay",
                  "Hasselblad X2D", "80mm f/2.8",
                  "Penthouse floor-to-ceiling windows — city below, the light in the room a combination of ambient city glow and a warm interior source.",
                  "Penthouse living area: floor-to-ceiling glass, the city grid below, modern furniture, the height creates a specific silence.",
                  "Neo at the window in burgundy, Shay beside him with her hand on the glass, both looking down at the city below. The scale of it making everything quiet and still."),
            scene(NEO_DESC, "Shay",
                  "Hasselblad X2D", "110mm f/2.0",
                  "Tight — their profiles against the city light, medium-format depth.",
                  "The city in beautiful out-of-focus light behind the glass.",
                  "Both in profile facing the window — Neo slightly behind, Shay's forehead just touching the glass. Two people and a city. Everything they need visible through one piece of glass."),
            scene(NEO_DESC, "Shay",
                  "Hasselblad X2D", "45mm f/3.5",
                  "Wider — the full penthouse space with the city through the glass.",
                  "The complete penthouse — the furniture, the windows, the city.",
                  "Wide — the penthouse and the view and the two people in it. The burgundy a warm counterpoint to the cool city glass."),
        ],
    },
    {
        "id": "neo_shay_studio_session",
        "partner": "Shay",
        "outfit": "NEO_OUTFITS/Fitness black set .png",
        "env": "NEO_ENVS/office setup.jpg",
        "caption": "She comes through to check on the vision. Every time. 🎬\n\nBuilding together.\n\n#studio #neo #couple #creativelife #vlm",
        "shots": [
            scene(NEO_DESC, "Shay",
                  "Sony A7 IV", "35mm f/1.8",
                  "Creative studio — the blue screen glow and warm practical lights creating a complex, layered light environment.",
                  "Neo's creative studio: multiple screens, creative tools, the organized chaos of someone who builds things seriously.",
                  "Neo at his setup, Shay leaning on the desk beside him looking at one of his screens. He's explaining something. She's listening. Creative partnership at its most natural."),
            scene(NEO_DESC, "Shay",
                  "Sony A7 IV", "85mm f/1.4",
                  "Tighter — both faces lit by the screen glow.",
                  "The studio equipment in bokeh.",
                  "Both looking at camera — Neo's studio behind them. She came to check on his work and the work checked out. The confidence of two people who trust each other's vision."),
            scene(NEO_DESC, "Shay",
                  "Sony A7 IV", "24mm f/2.8",
                  "Wide — the full studio, both of them in it.",
                  "The complete studio space — screens, equipment, the work.",
                  "Wide — Neo and Shay in the full studio environment. The place where things get made. The person who makes it all worth making."),
        ],
    },
    {
        "id": "neo_shay_runway_night",
        "partner": "Shay",
        "outfit": "NEO_OUTFITS/West Coast Floral Shirt .png",
        "env": "NEO_ENVS/neo runway.jpg",
        "caption": "Runway energy even when there's no runway 🌺\n\nHer editorial. My floral. Perfect balance.\n\n#runway #neo #couple #fashioncouple #aiinfluencer",
        "shots": [
            scene(NEO_DESC, "Shay",
                  "Canon EOS R5", "85mm f/1.2L",
                  "Night runway/event lighting — dramatic directional spots, deep shadows, high contrast.",
                  "An event space or runway area — dramatic lighting rigs, high ceilings, the architecture of spectacle.",
                  "Neo in West Coast floral, Shay in a complementary editorial look — both walking side by side toward camera with that specific energy of two people who know they look incredible together."),
            scene(NEO_DESC, "Shay",
                  "Canon EOS R5", "50mm f/1.4",
                  "The event lighting on both of them — high contrast, cinematic.",
                  "The event space behind them.",
                  "Both stopping to face camera — the spot light cutting a clean edge on Neo's shoulder, the floral catching the light beautifully. Shay's blonde bob luminous in the event light."),
            scene(NEO_DESC, "Shay",
                  "Canon EOS R5", "35mm f/2.8",
                  "Wider — the full event space, both of them in the environment.",
                  "The event space at full drama — the architecture, the light rigs, the scale.",
                  "Wide — Neo and Shay in the full dramatic space. Two people who look like they belong everywhere they are."),
        ],
    },

    # ── DAYS 11-20: Neo + Friends (Jazmine x2, Carli x2, Destiny x2, Sophia x2, Frannie x2) ──

    {
        "id": "neo_jazmine_tokyo_streets",
        "partner": "Jazmine",
        "outfit": "",
        "env": "ENVS/Tokyo Streets .jpg",
        "caption": "Tokyo with the right energy is a completely different city. Every single time.",
        "shots": [
            scene(NEO_DESC, "Jazmine",
                  "Leica M11", "35mm f/1.4 Summilux wide open",
                  "Tokyo evening — neon signs bleeding color across rain-slicked streets, warm and cool light fighting beautifully for dominance.",
                  "Shibuya-style crossing: neon kanji everywhere, the city at full sensory overload, wet pavement turning the street into a mirror.",
                  "Neo and Jazmine walking through the neon corridor — her long natural hair catching the colored light, both unbothered by the spectacle around them. Two people who are the most interesting thing on any block."),
            scene(NEO_DESC, "Jazmine",
                  "Leica M11", "50mm f/2.0 APO-Summicron",
                  "Under a Tokyo awning — the neon from outside reflecting on the wet concrete in front of them, complex overlapping color.",
                  "The Tokyo street in the background, the rain at the edges, the city still going.",
                  "Both turned toward each other mid-conversation — the neon painting their faces in competing warm and cool tones. The city is backdrop. The people are the story."),
            scene(NEO_DESC, "Jazmine",
                  "Leica M11", "28mm f/2.0",
                  "Wide — the full Tokyo chaos, rain, neon, motion.",
                  "The complete Tokyo environment: signs, pedestrians blurred in the distance, the wet street reflecting everything.",
                  "Wide — Neo and Jazmine small against the Tokyo night. The city enormous and alive around them. Kodak Portra 800 emulation, warm cast, natural grain, lifted blacks."),
        ],
    },
    {
        "id": "neo_jazmine_coffee_links",
        "partner": "Jazmine",
        "outfit": "",
        "env": "ENVS/Coffee shop aesthetic.jpg",
        "caption": "The conversations that happen over coffee that nobody films are always the best ones.",
        "shots": [
            scene(NEO_DESC, "Jazmine",
                  "Fujifilm GFX 100S", "63mm f/2.8",
                  "Coffee shop — soft north-facing window light, the diffuse warmth of a morning that isn't in a hurry.",
                  "Aesthetic coffee shop: exposed brick, wooden tables, ceramics, the kind of space that rewards conversation.",
                  "Neo and Jazmine across a small table — both leaning in, both talking at once, her warm smile taking over the frame. The coffee going cold. Neither noticing."),
            scene(NEO_DESC, "Jazmine",
                  "Fujifilm GFX 100S", "110mm f/2.0",
                  "Tight — both faces in the window light, medium-format rendering the skin tones with extraordinary depth.",
                  "The coffee shop bokeh warm behind.",
                  "Both looking at camera — caught in the middle of a good moment. Neo with his cup. Jazmine with her smile. The kind of frame you don't plan."),
            scene(NEO_DESC, "Jazmine",
                  "Fujifilm GFX 100S", "45mm f/3.5",
                  "Wide — the full coffee shop, both of them in it.",
                  "The complete coffee shop environment, the light falling across the whole scene.",
                  "Wide — Neo and Jazmine in the space. The best mornings have no agenda and the right person across the table."),
        ],
    },
    {
        "id": "neo_carli_art_gallery",
        "partner": "Carli",
        "outfit": "",
        "env": "ENVS/Art Gallery.jpg",
        "caption": "Art hits different when someone else is seeing it with you at the same time.",
        "shots": [
            scene(NEO_DESC, "Carli",
                  "Canon EOS R5", "85mm f/1.4",
                  "Gallery lighting — clean museum-grade directional light from above, the kind that makes art look like art and people look like portraits.",
                  "Modern gallery: white walls, large canvases, polished concrete, the beautiful weight of a room that takes things seriously.",
                  "Neo and Carli standing in front of a large abstract work — both actually looking at it, not at each other. Carli's fashion-forward energy next to Neo's creative director stillness. Two people in genuine attention."),
            scene(NEO_DESC, "Carli",
                  "Canon EOS R5", "50mm f/2.0",
                  "Gallery light natural and clean on both of them.",
                  "A striking canvas as the background in soft bokeh.",
                  "Both facing camera — the canvas behind them a burst of color against both their looks. Neo's curly hair soft under the gallery light. The art is also them."),
            scene(NEO_DESC, "Carli",
                  "Canon EOS R5", "35mm f/4",
                  "Wide — the gallery corridor, both of them moving through it.",
                  "The full gallery from end to end, canvases stretching the length of the room.",
                  "Wide — Neo and Carli walking the gallery. Not posing. Just moving from piece to piece the way you do when the work is actually good."),
        ],
    },
    {
        "id": "neo_carli_rooftop_golden",
        "partner": "Carli",
        "outfit": "",
        "env": "ENVS/Rooftop bar .jpg",
        "caption": "Rooftop. Golden hour. Someone worth talking to. That's the full list.",
        "shots": [
            scene(NEO_DESC, "Carli",
                  "Canon EOS R5", "85mm f/1.2L wide open at f/1.4",
                  "Rooftop bar at golden hour — the last horizontal light, warm orange washing across concrete and glass, the city below catching every photon.",
                  "Rooftop bar: elegant outdoor furniture, warm wood finishes, plants, the city as far as you can see.",
                  "Neo at the railing with Carli beside him — both with drinks, the city gold behind them. Her striking features catching the warm light exactly right. Both mid-thought, mid-sentence, mid-something good."),
            scene(NEO_DESC, "Carli",
                  "Canon EOS R5", "50mm f/1.8",
                  "Three-quarter front — warm backlight still washing the scene, soft city-glow fill.",
                  "The rooftop, the city shimmer, the golden haze.",
                  "Both looking at each other, the city behind them. Neo's beard catching the gold. Carli's look lit perfectly by the hour. The conversation better than anything on the skyline."),
            scene(NEO_DESC, "Carli",
                  "Canon EOS R5", "24mm f/4",
                  "Wide environmental — the full rooftop at dusk, city lights beginning to pop.",
                  "The complete rooftop scene, the vast city behind them, the sky going deep blue.",
                  "Wide — two figures against the city at magic hour. The scale is the point. The people are the point. Both simultaneously."),
        ],
    },
    {
        "id": "neo_destiny_maldives_pier",
        "partner": "Destiny",
        "outfit": "",
        "env": "ENVS/Maldives Pier Vibes .jpg",
        "caption": "Some places exist to remind you what perspective actually means.",
        "shots": [
            scene(NEO_DESC, "Destiny",
                  "Hasselblad X2D", "80mm f/2.8",
                  "Maldivian overwater pier at golden hour — the Andaman sun low and warm, the turquoise water refracting upward into a blue-green fill that doesn't exist anywhere else.",
                  "Maldives overwater pier: the bungalows stretching to the horizon, the water crystalline below, the sky doing everything it can.",
                  "Neo and Destiny at the end of the pier — both looking out at the open ocean, not at each other. Destiny's tall elegant frame and bone structure made for a Hasselblad. Both inside their own heads, the sea giving them room to think."),
            scene(NEO_DESC, "Destiny",
                  "Hasselblad X2D", "110mm f/2.0",
                  "Three-quarter front — the golden hour backlight behind them, medium-format rendering every detail.",
                  "The pier, the water, the distant bungalows in bokeh.",
                  "Both turning toward each other mid-conversation — Destiny's East African beauty and Neo's creative energy, the Maldives an absurdly perfect backdrop. A frame that shouldn't be real."),
            scene(NEO_DESC, "Destiny",
                  "Hasselblad X2D", "45mm f/4",
                  "Wide — the full Maldivian scene, two figures on the pier against the horizon.",
                  "The complete Maldives: the pier, the turquoise water, the bungalows, the enormous open sky.",
                  "Wide — Neo and Destiny small against the Maldivian seascape. Small in the best way. The world is enormous and beautiful. They are in it."),
        ],
    },
    {
        "id": "neo_destiny_luxury_lobby",
        "partner": "Destiny",
        "outfit": "",
        "env": "ENVS/Luxury Hotel Lobby .jpg",
        "caption": "Five-star lobbies were built for exactly this energy. You just have to show up correctly.",
        "shots": [
            scene(NEO_DESC, "Destiny",
                  "Hasselblad X2D", "80mm f/2.8",
                  "Luxury hotel lobby — chandeliers creating warm pools of light, marble reflecting everything back up, the architecture of money done with restraint.",
                  "A five-star hotel lobby: marble floors, enormous chandeliers, towering ceilings, the quiet confidence of extreme luxury.",
                  "Neo in high-fashion, Destiny in a luxury editorial look — both moving through the lobby with the ease of people who have been in beautiful rooms before. Her tall elegant frame commanding the marble corridor."),
            scene(NEO_DESC, "Destiny",
                  "Hasselblad X2D", "110mm f/2.0",
                  "The lobby chandelier light — warm and dimensional, medium-format depth.",
                  "The marble and chandelier light in gorgeous bokeh behind them.",
                  "Both facing camera — the architecture behind them making the portrait grander. Neo's curly hair and beard under the chandelier glow. Destiny's bone structure doing exactly what a camera needs it to do."),
            scene(NEO_DESC, "Destiny",
                  "Hasselblad X2D", "45mm f/3.5",
                  "Wide — the full lobby, both of them in it.",
                  "The complete hotel lobby — the scale of the ceiling, the marble, the light.",
                  "Wide — the lobby with its enormous proportions, Neo and Destiny in it. The architecture is impressive. The people in it more so."),
        ],
    },
    {
        "id": "neo_sophia_studio_collab",
        "partner": "Sophia",
        "outfit": "",
        "env": "NEO_ENVS/office setup.jpg",
        "caption": "The best creative partnerships don't look like meetings. They look like this.",
        "shots": [
            scene(NEO_DESC, "Sophia",
                  "Sony A7 IV", "35mm f/1.8",
                  "Creative studio — screen glow and warm practical lights creating a layered, dimensional light environment.",
                  "Neo's creative studio: multiple screens with work in progress, the organized intelligence of someone who builds things seriously.",
                  "Neo and Sophia both at the studio setup — she's looking at the screen with genuine interest, he's explaining something with his hands. Two different aesthetics, one shared creative frequency."),
            scene(NEO_DESC, "Sophia",
                  "Sony A7 IV", "85mm f/1.4",
                  "Tight — both faces lit by the screen glow, dimensional and cinematic.",
                  "The studio equipment soft in bokeh behind them.",
                  "Both facing camera from the studio — Neo's creative director energy next to Sophia's bright, chic presence. The work behind them. The confidence between them."),
            scene(NEO_DESC, "Sophia",
                  "Sony A7 IV", "24mm f/2.8",
                  "Wide — the full studio, both of them in it.",
                  "The complete studio environment — the screens, the equipment, the work.",
                  "Wide — Neo and Sophia in the studio. The space that holds the vision. The people who are building it."),
        ],
    },
    {
        "id": "neo_sophia_front_yard",
        "partner": "Sophia",
        "outfit": "",
        "env": "NEO_ENVS/front yard.jpg",
        "caption": "No agenda. No schedule. Just good energy and somewhere to sit. That's a perfect day.",
        "shots": [
            scene(NEO_DESC, "Sophia",
                  "Canon EOS R5", "50mm f/2.0",
                  "Outdoor afternoon — warm directional sun at 45°, the quality of natural light that photographers chase and rarely catch.",
                  "Front yard: grass, trees, the organic ease of being outside with no reason to go anywhere.",
                  "Neo on the steps, Sophia on the grass beside him — both mid-conversation, completely relaxed. Her chic ease against his creative director calm. The afternoon light doing everything right."),
            scene(NEO_DESC, "Sophia",
                  "Canon EOS R5", "85mm f/1.4",
                  "Warm outdoor light on both faces — the best natural fill.",
                  "The yard and trees in soft bokeh behind them.",
                  "Both looking at camera — caught in the middle of the afternoon, unposed. Two people who are genuinely comfortable. The light earned it."),
            scene(NEO_DESC, "Sophia",
                  "Canon EOS R5", "35mm f/4",
                  "Wide outdoor — the full yard scene.",
                  "The complete outdoor environment: grass, trees, the afternoon.",
                  "Wide — the yard, the afternoon, two people with nowhere to be. The simplest things are always the most photogenic."),
        ],
    },
    {
        "id": "neo_frannie_penthouse_night",
        "partner": "Frannie",
        "outfit": "",
        "env": "ENVS/Penthouse View .jpg",
        "caption": "A city looks completely different from up here. So does everything else.",
        "shots": [
            scene(NEO_DESC, "Frannie",
                  "Canon EOS R5", "85mm f/1.2L wide open",
                  "Penthouse floor-to-ceiling windows at night — the city grid below, interior warm light creating a split: warm inside, cool city outside.",
                  "Penthouse living area: floor-to-ceiling glass, the entire city visible below, modern furniture, the height creates a specific silence.",
                  "Neo at the window, Frannie beside him — her expressive Latina energy and his creative director stillness making a natural contrast. Both looking out at the city below, the glass between them and all of it."),
            scene(NEO_DESC, "Frannie",
                  "Canon EOS R5", "50mm f/1.4",
                  "Tight — both profiles against the city light, the warm interior behind them.",
                  "The city grid in soft out-of-focus light through the glass.",
                  "Both turned slightly toward each other — the city as backdrop. Neo's curly hair and beard in the window light. Frannie's dark hair catching the warm interior glow. A frame about the view and the people seeing it."),
            scene(NEO_DESC, "Frannie",
                  "Canon EOS R5", "35mm f/2.8",
                  "Wide — the full penthouse space, the city through the glass.",
                  "The complete penthouse: the furniture, the windows, the city.",
                  "Wide — the penthouse, the view, and the two people who earned being here. Everything placed correctly."),
        ],
    },
    {
        "id": "neo_frannie_beach_golden",
        "partner": "Frannie",
        "outfit": "",
        "env": "ENVS/Beach Vibes Tropics.jpg",
        "caption": "The beach at golden hour is one of those things that never stops working.",
        "shots": [
            scene(NEO_DESC, "Frannie",
                  "Canon EOS R5", "85mm f/1.4",
                  "Tropical beach at golden hour — horizontal light, warm pink and gold, the water glassy and warm.",
                  "Tropical beach: the sand clean and empty, the water catching the last light, the colors you don't see unless you stay for them.",
                  "Neo and Frannie at the water's edge — both standing with the sunset in front of them. Her infectious energy softened to something quieter by the golden hour. His curly hair backlit. A moment before whatever comes next."),
            scene(NEO_DESC, "Frannie",
                  "Canon EOS R5", "50mm f/1.8",
                  "The golden hour glow warm on both of them — directional and perfect.",
                  "The tropical water and beach in soft focus behind.",
                  "Both sitting on the sand, facing the ocean — Frannie animated mid-laugh, Neo watching her, smiling. The beach at its best is always about the people in it."),
            scene(NEO_DESC, "Frannie",
                  "Canon EOS R5", "24mm f/4",
                  "Wide — the full tropical beach at golden hour, two figures in it.",
                  "The beach at its most expansive: the water, the sky, the light.",
                  "Wide — their silhouettes against the golden water. Two people who made time for this. The beach made time for them."),
        ],
    },

    # ── DAYS 21-25: Neo + Jazmine / Carli (friend energy) ────────────────────

    {
        "id": "neo_jazmine_streetwear",
        "partner": "Jazmine",
        "outfit": "NEO_OUTFITS/Brow Jordan hoodie.png",
        "env": "ENVS/Urban Streetwear .jpg",
        "caption": "Street energy needs the right co-star 🔥\n\n#neo #streetwear #jordan #urban #style",
        "shots": [
            scene(NEO_DESC, "Jazmine",
                  "Sony A7 IV", "35mm f/1.8",
                  "Urban street — overcast flat light, the streetwear photographer's best friend. Uniform, detail-faithful, no harsh shadows.",
                  "Urban environment: concrete, murals, the texture of a city that works.",
                  "Neo in the brown Jordan hoodie, Jazmine in complementary streetwear — both against the urban backdrop, energy relaxed and authentic. Street photography rules: let the clothes and the people do the work."),
            scene(NEO_DESC, "Jazmine",
                  "Sony A7 IV", "85mm f/1.4",
                  "Tight on both — the street light clean on their faces.",
                  "Urban concrete and murals behind.",
                  "Both facing camera — Neo and Jazmine. The brown Jordan and Jazmine's streetwear. Two people who dress correctly without overthinking it."),
            scene(NEO_DESC, "Jazmine",
                  "Sony A7 IV", "24mm f/2.8",
                  "Wide urban — the full street environment.",
                  "The complete urban scene.",
                  "Wide — Neo and Jazmine in the city. The street belongs to them."),
        ],
    },
    {
        "id": "neo_jazmine_afternoon_vibes",
        "partner": "Jazmine",
        "outfit": "NEO_OUTFITS/Simple Every Day slides.jpg",
        "env": "ENVS/Outdoor Seating .jpg",
        "caption": "Some afternoons you just need a friend and a good spot 🌿\n\n#neo #afternoon #hangout #vibes #friends",
        "shots": [
            scene(NEO_DESC, "Jazmine",
                  "Fujifilm X-T5", "56mm f/1.2",
                  "Outdoor afternoon — warm dappled light through trees, the best accidental lighting money cannot buy.",
                  "Outdoor seating area: wood tables, plants, the casual luxury of a place with good energy.",
                  "Neo and Jazmine at an outdoor table — both relaxed, both mid-laugh at something. The slides under the table, the afternoon around them. Unforced."),
            scene(NEO_DESC, "Jazmine",
                  "Fujifilm X-T5", "56mm f/1.4",
                  "The warm dappled light on both faces.",
                  "The outdoor space behind them.",
                  "Both looking at camera from their chairs — caught in the middle of a good afternoon. The slides, the outdoors, the easy energy."),
            scene(NEO_DESC, "Jazmine",
                  "Fujifilm X-T5", "23mm f/2.8",
                  "Wide — the full outdoor setting.",
                  "The complete outdoor scene with trees and light.",
                  "Wide — Neo and Jazmine in the outdoor space. Some afternoons are just for this."),
        ],
    },
    {
        "id": "neo_carli_gallery_walk",
        "partner": "Carli",
        "outfit": "NEO_OUTFITS/mens fsll brown fit.png",
        "env": "ENVS/Art Gallery.jpg",
        "caption": "The culture never takes a day off and neither do we 🎨\n\n#neo #artgallery #culture #style #friends",
        "shots": [
            scene(NEO_DESC, "Carli",
                  "Leica Q3", "28mm f/1.7",
                  "Gallery lighting — the clean directional museum light.",
                  "Modern gallery: white walls, large important-looking canvases.",
                  "Neo and Carli in the gallery — she's closer to a canvas, studying it. He's behind and to the right, watching her look at it. A moment of shared attention that isn't directed at camera."),
            scene(NEO_DESC, "Carli",
                  "Leica Q3", "28mm f/2.0",
                  "The gallery light on both.",
                  "A large canvas behind.",
                  "Both facing camera from the gallery — the fall brown and Carli's gallery look. Two people who take culture seriously."),
            scene(NEO_DESC, "Carli",
                  "Leica Q3", "28mm f/4",
                  "Wide gallery.",
                  "The gallery corridor at full length.",
                  "Wide — Neo and Carli moving through the gallery. The white walls and big canvases making everything feel important."),
        ],
    },
    {
        "id": "neo_carli_luxury_lunch",
        "partner": "Carli",
        "outfit": "NEO_OUTFITS/Louis Vutton Brown fit .png",
        "env": "ENVS/Luxury Outdoor Dining .jpg",
        "caption": "Lunch that hits every sense. ☀️\n\n#neo #lunch #luxury #outdoor #style",
        "shots": [
            scene(NEO_DESC, "Carli",
                  "Canon EOS R5", "85mm f/1.4",
                  "Outdoor luxury dining — midday sun softened by a market umbrella, warm and flattering.",
                  "Luxury outdoor dining: white tablecloths, the sound of clinking glasses, greenery, the Mediterranean aesthetic.",
                  "Neo at a luxury outdoor table with Carli — Louis V brown, her in a summer lunch look, both with food in front of them. The outdoor sun making everything warm and correct."),
            scene(NEO_DESC, "Carli",
                  "Canon EOS R5", "50mm f/1.8",
                  "The lunch table light — umbrella diffused, warm.",
                  "The outdoor dining scene behind them.",
                  "Both facing camera from the table — the LV brown and Carli's look. The food visible. The luxury casual."),
            scene(NEO_DESC, "Carli",
                  "Canon EOS R5", "35mm f/4",
                  "Wide — the full outdoor dining setting.",
                  "The complete luxury outdoor dining scene.",
                  "Wide — the table, the greenery, the sky, two people having a very good lunch."),
        ],
    },
    {
        "id": "neo_destiny_downtown",
        "partner": "Destiny",
        "outfit": "NEO_OUTFITS/Everyday black and Red .png",
        "env": "ENVS/Urban Streetwear .jpg",
        "caption": "Downtown energy with the right person elevates everything 🖤\n\n#neo #downtown #urban #style #friends",
        "shots": [
            scene(NEO_DESC, "Destiny",
                  "Sony A7 IV", "35mm f/2.0",
                  "Downtown overcast — the flat even light of a working city, perfect for editorial street work.",
                  "Downtown urban environment: glass towers, concrete, the pace of a city moving.",
                  "Neo and Destiny downtown — the black and red against the urban concrete, her East African elegance beside his creative director energy. Two people the city notices."),
            scene(NEO_DESC, "Destiny",
                  "Sony A7 IV", "85mm f/1.4",
                  "The downtown light on both.",
                  "Urban concrete behind.",
                  "Both facing camera downtown — Neo and Destiny. The black and red. Her striking features in the downtown light."),
            scene(NEO_DESC, "Destiny",
                  "Sony A7 IV", "24mm f/3.5",
                  "Wide — the full downtown.",
                  "The city at full urban scale.",
                  "Wide — Neo and Destiny in the downtown. The city as backdrop, them as foreground. The correct ratio."),
        ],
    },

    # ── DAYS 26-30: Neo + Shay (closing strong) ───────────────────────────────

    {
        "id": "neo_shay_home_evening",
        "partner": "Shay",
        "outfit": "NEO_OUTFITS/Simple Tanke and Green .png",
        "env": "ENVS/Shays Kitchen.jpg",
        "caption": "Home is wherever this is 🏡\n\nEvening > morning because she's here for both.\n\n#neo #home #couple #evening #domesticbliss",
        "shots": [
            scene(NEO_DESC, "Shay",
                  "Fujifilm GFX 100S", "63mm f/2.8",
                  "Home evening — warm practical light, the kind of golden glow that only exists in homes in the evening.",
                  "Home living space: warm tones, comfortable furniture, the lived-in quality of a real home.",
                  "Neo and Shay at home in the evening — he's on the sofa, she's pulling him up from it, the evening light making everything warm. Real domesticity, not posed."),
            scene(NEO_DESC, "Shay",
                  "Fujifilm GFX 100S", "110mm f/2.0",
                  "The home light warm and close.",
                  "The home in soft focus behind.",
                  "Both on the sofa together — Shay with her feet tucked up, Neo's arm around her. Both looking at camera. The tank and green. Her blonde bob. Home."),
            scene(NEO_DESC, "Shay",
                  "Fujifilm GFX 100S", "45mm f/3.5",
                  "Wider — the full home scene.",
                  "The living space in context.",
                  "Wide — the home, the evening light, the two people in it. The best version of any day ends like this."),
        ],
    },
    {
        "id": "neo_shay_europe_cobblestone",
        "partner": "Shay",
        "outfit": "NEO_OUTFITS/Brown Travis outfit.png",
        "env": "ENVS/European Cobblestone Street .jpg",
        "caption": "Europe gave us exactly what we needed 🇪🇺\n\nThe cobblestones. The light. Her.\n\n#neo #europe #travel #couple #luxury",
        "shots": [
            scene(NEO_DESC, "Shay",
                  "Leica M11", "35mm f/1.4 Summilux",
                  "European afternoon — the golden hour light bouncing off limestone and cobblestone, warming everything it touches.",
                  "European cobblestone street: narrow, historic, window boxes, the architecture of centuries of good taste.",
                  "Neo in Travis brown, Shay in a European afternoon look — walking the cobblestone street, his hand in hers, both looking at something off camera with that tourist-who-actually-sees-things expression."),
            scene(NEO_DESC, "Shay",
                  "Leica M11", "50mm f/2.0 APO-Summicron",
                  "The European golden light on both of them.",
                  "Cobblestones and historic buildings behind.",
                  "Both facing camera on the cobblestone street — the Travis brown and her European look. The Leica rendering everything with that specific quality only Leica has."),
            scene(NEO_DESC, "Shay",
                  "Leica M11", "28mm f/2.0",
                  "Wide — the full European street.",
                  "The cobblestone street with historic architecture at full length.",
                  "Wide — the European street, the golden hour, two people walking it. The kind of afternoon you go somewhere for."),
        ],
    },
    {
        "id": "neo_shay_private_event",
        "partner": "Shay",
        "outfit": "NEO_OUTFITS/Mens High Fashion/mens high fashion 1.jpg",
        "env": "ENVS/Private Event .jpg",
        "caption": "The kind of events they don't publicize 🎉\n\nYou just end up there with the right people.\n\n#neo #event #couple #luxury #vlm",
        "shots": [
            scene(NEO_DESC, "Shay",
                  "Canon EOS R5", "85mm f/1.2L",
                  "Private event — warm ambient lighting, candlelight and soft fixtures, the light of a curated gathering.",
                  "A private event space: flowers, soft lighting, beautiful people in the background, the atmosphere of somewhere exclusive.",
                  "Neo in high fashion with Shay in an event look — both at the event, his hand on the small of her back, both mid-conversation with someone just off frame. The real event energy: not performing, just being."),
            scene(NEO_DESC, "Shay",
                  "Canon EOS R5", "50mm f/1.4",
                  "The event ambient light on both of them.",
                  "The event space behind them.",
                  "Both facing camera from the event — the high fashion and Shay's event look. The couple that arrives and the room notices."),
            scene(NEO_DESC, "Shay",
                  "Canon EOS R5", "35mm f/2.8",
                  "Wider — the full event scene.",
                  "The complete private event space.",
                  "Wide — Neo and Shay in the private event. The whole room around them."),
        ],
    },
    {
        "id": "neo_shay_airport",
        "partner": "Shay",
        "outfit": "NEO_OUTFITS/Rick Owens Fit .jpg",
        "env": "ENVS/Airport Luxury .jpg",
        "caption": "Every takeoff feels like the beginning of something 🛫\n\nHer + Rick + anywhere. The formula.\n\n#neo #airport #travel #couple #rickowens",
        "shots": [
            scene(NEO_DESC, "Shay",
                  "Leica Q3", "28mm f/1.7",
                  "Airport — the specific quality of airport light: overcast, even, slightly cool. Travelers at their most documentary-real.",
                  "Luxury airport terminal: floor-to-ceiling windows, the tarmac and planes visible, the organized chaos of transit.",
                  "Neo in Rick Owens, Shay beside him with carry-on — both moving through the terminal with the ease of people who travel often enough that airports don't impress them. Only the destination does."),
            scene(NEO_DESC, "Shay",
                  "Leica Q3", "28mm f/2.0",
                  "The airport windows behind them — planes on the tarmac, the outside light filtering in.",
                  "The terminal windows and the planes beyond.",
                  "Both at the gate — Neo's Rick Owens drape against Shay's travel look. Both looking out at the tarmac. Somewhere they're going that doesn't exist yet."),
            scene(NEO_DESC, "Shay",
                  "Leica Q3", "28mm f/4",
                  "Wide — the full terminal.",
                  "The airport terminal at full scale — people moving, planes through the glass.",
                  "Wide — the terminal, the planes, two people about to be somewhere else. The beginning of a trip is its own kind of anticipation."),
        ],
    },
    {
        "id": "neo_shay_closing_rooftop",
        "partner": "Shay",
        "outfit": "NEO_OUTFITS/Louis Vutton Brown fit .png",
        "env": "ENVS/Rooftop bar .jpg",
        "caption": "30 days. Every day with her. That's the whole story. 🌃\n\n#neo #30days #couple #rooftop #vlm #aiinfluencer",
        "shots": [
            scene(NEO_DESC, "Shay",
                  "Hasselblad X2D", "80mm f/2.8",
                  "Rooftop at night — the city full below, soft warm rooftop bar lighting, the sky dark and the city electric.",
                  "Rooftop bar at night: the city a carpet of light below, the bar itself warmly lit, the contrast of warm and electric all around them.",
                  "Neo in Louis V brown with Shay in a night look — both at the rooftop bar railing, the city below them. His arm around her. Both looking out at the city they've moved through for 30 days. The LV brown luminous in the rooftop light."),
            scene(NEO_DESC, "Shay",
                  "Hasselblad X2D", "110mm f/2.0",
                  "The night rooftop light — warm, medium-format depth.",
                  "The city lights in bokeh below.",
                  "Both facing camera from the rooftop at night — Neo and Shay. The LV brown and her night look. The city behind them. 30 days of this. Every day earned."),
            scene(NEO_DESC, "Shay",
                  "Hasselblad X2D", "45mm f/3.5",
                  "Wide — the full night rooftop with the city below.",
                  "The complete rooftop bar scene at night with the city.",
                  "Wide — the rooftop, the city at night, two people at the railing. The closing frame of 30 days of showing up. They'll be back tomorrow."),
        ],
    },
]


def resolve(path_str: str) -> str:
    s = str(path_str)
    s = s.replace("NEO_OUTFITS/", str(NEO_OUTFITS) + "/")
    s = s.replace("NEO_ENVS/", str(NEO_ENVS) + "/")
    s = s.replace("ENVS_2026/", str(ENVS_2026) + "/")
    s = s.replace("ENVS/", str(ENVS) + "/")
    return s


def build_assets(carousel: dict, carousel_idx: int) -> list:
    partner = carousel["partner"]
    assets = [
        {"path": str(NEO_HERO), "label": "Main Character: Neo"},
    ]
    for ref_path in FRIEND_REFS.get(partner, []):
        if os.path.exists(ref_path):
            assets.append({"path": ref_path, "label": f"Cast: {partner}"})

    # Rotate through ALL Neo outfits by carousel index
    if NEO_ALL_OUTFITS:
        neo_outfit = NEO_ALL_OUTFITS[carousel_idx % len(NEO_ALL_OUTFITS)]
        assets.append({"path": str(neo_outfit), "label": "Outfit for Main Character"})

    # Also pass an outfit for the partner (Shay or Angeil) if we have one
    pool = PARTNER_OUTFIT_POOL.get(partner, [])
    if pool:
        offset = len(pool) // 3
        partner_outfit = pool[(carousel_idx + offset) % len(pool)]
        assets.append({"path": str(partner_outfit), "label": f"Outfit for {partner}"})

    env_path = resolve(carousel.get("env", "")) if carousel.get("env") else ""
    if env_path and os.path.exists(env_path):
        assets.append({"path": env_path, "label": "Scene Location/Vibe"})

    return assets


def main():
    print("🎬 Neo — 30-Day Carousel Generator (MASTER REWRITE)")
    print(f"Output: {OUTPUT}\n")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    total = len(CAROUSELS)

    for i, carousel in enumerate(CAROUSELS):
        cid = carousel["id"]
        partner = carousel["partner"]
        print(f"\n{'='*60}")
        print(f"[{i+1}/{total}] {cid} | Cast: Neo + {partner}")
        print(f"{'='*60}")

        caption_path = OUTPUT / f"{cid}_caption.txt"
        neo_cta = (
            "\n\nAI-powered. Human-directed. This is what the new creative economy looks like — "
            "built with intention, documented in real time, scaled with technology.\n\n"
            "We build AI content brands at vlmcreateflow.com 🤖\n"
            "DM us or visit the link in bio to get started."
        )
        caption_path.write_text(carousel["caption"] + neo_cta)

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
                    "cast": ["Neo", partner],
                    "cast_count": 2,
                    "cast_refs": {
                        "Neo": [str(NEO_HERO)],
                        partner: FRIEND_REFS.get(partner, []),
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
