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
    "Angeil":   [str(ANGEIL_HERO), str(ANGEIL_EYES)],
    "Jazmine":  [str(FRIENDS_DIR / "Jazmine.jpg")],
    "Carli":    [str(FRIENDS_DIR / "Carli.jpg")],
    "Destiny":  [str(FRIENDS_DIR / "East African Rich Girl .jpg")],
    "MixedBabe":[str(FRIENDS_DIR / "Pretty curly long mixed Girl .jpg")],
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
    "Angeil":   "Beautiful Black woman, melanin-rich skin, natural or styled dark hair, modelesque frame — radiating creative intelligence and warmth. A collaborator, not a prop.",
    "Jazmine":  "Stunning Black woman, warm brown skin, long natural hair, warm smile — confidence and joy in equal measure.",
    "Carli":    "Beautiful Black woman, deep warm complexion, striking features, fashion-forward energy.",
    "Destiny":  "Beautiful East African woman, stunning bone structure, tall and elegant — the kind of presence that photographers orbit.",
    "MixedBabe":"Beautiful mixed woman, curly hair, warm complexion, effortlessly magnetic.",
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

    # ── DAYS 11-20: Neo + Angeil (creative partner energy) ───────────────────

    {
        "id": "neo_angeil_creative_studio",
        "partner": "Angeil",
        "outfit": "NEO_OUTFITS/Simple Tanke and Green .png",
        "env": "NEO_ENVS/office setup.jpg",
        "caption": "The creative collaboration sessions that don't make it online 🎬\n\nWhen the work is that good, you stay longer.\n\n#neo #creative #collab #studio #vlm",
        "shots": [
            scene(NEO_DESC, "Angeil",
                  "Sony A7 IV", "35mm f/1.8",
                  "Studio — screen glow and warm practical lights, the focused light of two people deep in work.",
                  "Creative studio: screens with work in progress, the organized intelligence of a serious creative environment.",
                  "Neo and Angeil both looking at a screen — her pointing at something, him nodding. The collaboration is real and visible. Two creative minds in alignment."),
            scene(NEO_DESC, "Angeil",
                  "Sony A7 IV", "85mm f/1.4",
                  "Tight on both faces — the screen glow creating dimensional light.",
                  "The studio equipment soft behind.",
                  "Both facing camera from the studio — Neo in the tank and green, Angeil in a creative look. The kind of confidence that only comes from building something real together."),
            scene(NEO_DESC, "Angeil",
                  "Sony A7 IV", "24mm f/2.8",
                  "Wide — the full studio space, both of them in it.",
                  "The complete studio environment.",
                  "Wide — Neo and Angeil in the studio. Everything they're making visible in the space around them."),
        ],
    },
    {
        "id": "neo_angeil_art_walk",
        "partner": "Angeil",
        "outfit": "NEO_OUTFITS/mens fsll brown fit.png",
        "env": "ENVS/Art Gallery.jpg",
        "caption": "Art walk with the right person changes how you see everything 🖼️\n\n#neo #artgallery #creative #culture #vlm",
        "shots": [
            scene(NEO_DESC, "Angeil",
                  "Leica Q3", "28mm f/1.7",
                  "Gallery lighting — clean directional museum light, their faces lit from above and to the left.",
                  "Modern gallery: white walls, large canvases, the beautiful silence of curation.",
                  "Neo and Angeil walking slowly through the gallery — he's gesturing toward a piece, she's listening intently. Two people who actually see things."),
            scene(NEO_DESC, "Angeil",
                  "Leica Q3", "28mm f/2.0",
                  "The gallery light natural and clean.",
                  "A striking canvas in the background.",
                  "Both in front of a large canvas, both looking at it — their backs to camera. The scale of the canvas. The scale of their attention."),
            scene(NEO_DESC, "Angeil",
                  "Leica Q3", "28mm f/2.8",
                  "Wide gallery corridor light.",
                  "The full gallery from end to end.",
                  "Wide — Neo and Angeil in the gallery corridor. Two people who move through cultural spaces with ease."),
        ],
    },
    {
        "id": "neo_angeil_rooftop_sunset",
        "partner": "Angeil",
        "outfit": "NEO_OUTFITS/Orange BA Fit .jpg",
        "env": "ENVS/Rooftop bar .jpg",
        "caption": "Sunset from up here hits different when the conversation is right 🧡\n\n#neo #rooftop #sunset #creative #vibes",
        "shots": [
            scene(NEO_DESC, "Angeil",
                  "Canon EOS R5", "85mm f/1.4",
                  "Rooftop bar at sunset — the orange hour, warm directional light coming in low from the west.",
                  "Rooftop bar: elegant outdoor furniture, city behind, plants and warm wood finishes, the amber of golden hour everywhere.",
                  "Neo in the orange fit at the rooftop bar with Angeil — both with drinks, both mid-conversation. The orange of his fit resonating with the golden hour around them. Almost compositionally designed by the universe."),
            scene(NEO_DESC, "Angeil",
                  "Canon EOS R5", "50mm f/1.8",
                  "Warm golden hour light on both of them.",
                  "The rooftop and city behind them.",
                  "Both facing camera from the rooftop — the sunset making everything warm and correct. Neo's orange fit against Angeil's look. Two people at ease."),
            scene(NEO_DESC, "Angeil",
                  "Canon EOS R5", "35mm f/4",
                  "Wide — the full rooftop bar at golden hour.",
                  "The complete rooftop bar scene with city view.",
                  "Wide — the rooftop bar, the city, the golden hour light. Neo and Angeil small in the big beautiful scene."),
        ],
    },
    {
        "id": "neo_angeil_fashion_week",
        "partner": "Angeil",
        "outfit": "NEO_OUTFITS/Hoop Fit 1 Pink AE.png",
        "env": "NEO_ENVS/neo runway.jpg",
        "caption": "Fashion week energy every week of the year 💕\n\n#neo #fashionweek #style #creative #vlm",
        "shots": [
            scene(NEO_DESC, "Angeil",
                  "Canon EOS R5", "85mm f/1.2L",
                  "Fashion event lighting — dramatic directional spots, runway-quality light.",
                  "A fashion event space: the architecture of spectacle, elevated crowd energy.",
                  "Neo in the pink AE hoop fit, Angeil in an editorial look — both at the event with the energy of people who belong in every room they enter."),
            scene(NEO_DESC, "Angeil",
                  "Canon EOS R5", "50mm f/1.4",
                  "The event spots on both of them.",
                  "The event behind them.",
                  "Both facing camera — the pink fit and Angeil's look. Fashion event faces. Not trying. Just being."),
            scene(NEO_DESC, "Angeil",
                  "Canon EOS R5", "35mm f/2.8",
                  "Wider — the full event space.",
                  "The event space in full effect.",
                  "Wide — Neo and Angeil in the fashion event. Two people who make any room look like it was designed for them."),
        ],
    },
    {
        "id": "neo_angeil_coffee_shop",
        "partner": "Angeil",
        "outfit": "NEO_OUTFITS/Cowprint SLide Brown Fit .png",
        "env": "ENVS/Coffee shop aesthetic.jpg",
        "caption": "Creative conversations need the right setting ☕\n\nThe work never stops when the energy is right.\n\n#neo #coffeeshop #creative #collab #morning",
        "shots": [
            scene(NEO_DESC, "Angeil",
                  "Fujifilm X-T5", "56mm f/1.2",
                  "Coffee shop — natural window light, warm, soft, the texture of a working morning.",
                  "Aesthetic coffee shop: exposed brick, wooden tables, the organized beauty of a place built for thinking.",
                  "Neo and Angeil across a table from each other — notebooks and laptops between them, both animated in conversation. The cowprint slides under the table. Working in the best possible way."),
            scene(NEO_DESC, "Angeil",
                  "Fujifilm X-T5", "56mm f/1.4",
                  "Warmer window light, the coffee in frame.",
                  "The coffee shop aesthetic behind them.",
                  "Both with their coffee cups — not posed, caught mid-moment. The work and the warmth of the space around them."),
            scene(NEO_DESC, "Angeil",
                  "Fujifilm X-T5", "23mm f/2.0",
                  "Wide — the full coffee shop, both of them in it.",
                  "The complete coffee shop environment.",
                  "Wide — Neo and Angeil in the coffee shop, the work spread on the table, the space holding them well."),
        ],
    },
    {
        "id": "neo_angeil_front_yard",
        "partner": "Angeil",
        "outfit": "NEO_OUTFITS/mens shorts red marlbror .jpg",
        "env": "NEO_ENVS/front yard.jpg",
        "caption": "Some of the best conversations happen outside with nowhere to be 🌿\n\n#neo #outdoor #hangout #creative #vlm",
        "shots": [
            scene(NEO_DESC, "Angeil",
                  "Canon EOS R5", "50mm f/2.0",
                  "Outdoor afternoon — warm directional sun at 45°, the quality of light that makes everything feel effortless.",
                  "A front yard or outdoor space: grass, trees, the natural ease of being outside with no agenda.",
                  "Neo and Angeil sitting outside — him on the steps, her on the grass beside him. Mid-conversation, relaxed, nowhere to be. The red Marlboro shorts a casual note in an outdoor scene."),
            scene(NEO_DESC, "Angeil",
                  "Canon EOS R5", "85mm f/1.4",
                  "Warm outdoor light on both faces.",
                  "The yard and trees behind them.",
                  "Both looking at camera from their outdoor spots — unposed, just looked over. The ease of two people who are comfortable in each other's presence."),
            scene(NEO_DESC, "Angeil",
                  "Canon EOS R5", "35mm f/4",
                  "Wide outdoor — the full yard.",
                  "The complete outdoor scene.",
                  "Wide — the yard, the afternoon, two people with no agenda. Perfect."),
        ],
    },
    {
        "id": "neo_angeil_luxury_lobby",
        "partner": "Angeil",
        "outfit": "NEO_OUTFITS/Mens High Fashion/mens high fashion 1.jpg",
        "env": "ENVS/Luxury Hotel Lobby .jpg",
        "caption": "Five-star lobbies were built for moments like this 🏛️\n\n#neo #luxury #hotel #style #creative",
        "shots": [
            scene(NEO_DESC, "Angeil",
                  "Hasselblad X2D", "80mm f/2.8",
                  "Luxury hotel lobby — chandeliers creating warm pools of light, marble reflecting it all.",
                  "A five-star hotel lobby: marble floors, enormous chandeliers, the architectural confidence of extreme luxury.",
                  "Neo in high fashion, Angeil in a luxury look — both in the lobby, both moving with the ease of people who have been in beautiful rooms before and will be again."),
            scene(NEO_DESC, "Angeil",
                  "Hasselblad X2D", "110mm f/2.0",
                  "The lobby light — warm chandelier light, medium-format rendering.",
                  "The marble and the light in bokeh.",
                  "Both facing camera in the lobby — the architecture behind them making the portrait grander. Neo's high fashion and Angeil's look. Two people who elevate any room."),
            scene(NEO_DESC, "Angeil",
                  "Hasselblad X2D", "45mm f/3.5",
                  "Wide — the full lobby, both of them in it.",
                  "The complete hotel lobby — the scale of it.",
                  "Wide — the lobby with its enormous proportions, Neo and Angeil in it. The architecture is impressive. They're more impressive."),
        ],
    },
    {
        "id": "neo_angeil_pool_day",
        "partner": "Angeil",
        "outfit": "NEO_OUTFITS/green swim shorts .jpg",
        "env": "ENVS/Pool Party .jpg",
        "caption": "Pool days with the right energy are different 💧\n\n#neo #poolday #summer #creative #vlm",
        "shots": [
            scene(NEO_DESC, "Angeil",
                  "Canon EOS R5", "50mm f/1.8",
                  "Poolside midday — clean overhead sun, the water bouncing light upward creating that specific pool shimmer.",
                  "Luxury pool area: blue water, sun loungers, the organized pleasure of a beautiful pool.",
                  "Neo at the pool edge in green swim shorts, Angeil beside him — both in the water up to their waists, both looking at camera. The pool light doing everything it should."),
            scene(NEO_DESC, "Angeil",
                  "Canon EOS R5", "85mm f/1.4",
                  "The pool light — bounced from the water surface, extraordinary.",
                  "The pool blue behind them.",
                  "Both at the pool edge, the water light playing across their faces. The green shorts against the blue water. Color perfect."),
            scene(NEO_DESC, "Angeil",
                  "Canon EOS R5", "35mm f/5.6",
                  "Wide — the full pool scene.",
                  "The complete pool environment.",
                  "Wide — the pool, the sun, two people in it. Exactly what summer should look like."),
        ],
    },
    {
        "id": "neo_angeil_skyline_dinner",
        "partner": "Angeil",
        "outfit": "NEO_OUTFITS/Brown luis v .png",
        "env": "ENVS/Skyline Restaurant .jpg",
        "caption": "Dinner with a view and the right company. Unmatched. 🍽️\n\n#neo #dinner #skyline #luxury #creative",
        "shots": [
            scene(NEO_DESC, "Angeil",
                  "Fujifilm GFX 100S", "63mm f/2.8",
                  "Skyline restaurant — the city at night through floor-to-ceiling windows, the interior lit warm and intimate.",
                  "A skyline restaurant: white tablecloths, the city glowing beyond the glass, wine in crystal, the kind of place where conversation matters.",
                  "Neo and Angeil at the dinner table — the city behind them, the table between them, both leaning in slightly. The conversation is the main course."),
            scene(NEO_DESC, "Angeil",
                  "Fujifilm GFX 100S", "110mm f/2.0",
                  "The warm restaurant light on both faces.",
                  "The city in bokeh through the glass.",
                  "Both facing camera from the table — the Louis V brown and Angeil's dinner look. Two people who know how to dress for a room."),
            scene(NEO_DESC, "Angeil",
                  "Fujifilm GFX 100S", "45mm f/3.5",
                  "Wide — the full restaurant with the city view.",
                  "The complete skyline restaurant scene.",
                  "Wide — the restaurant, the city, the table, the two people at it. Everything placed correctly."),
        ],
    },
    {
        "id": "neo_angeil_maldives",
        "partner": "Angeil",
        "outfit": "NEO_OUTFITS/green swim shorts .jpg",
        "env": "ENVS/Maldives Pier Vibes .jpg",
        "caption": "Maldives creative retreat. Zero schedule. Maximum output. 🌊\n\n#neo #maldives #travel #creative #vlm",
        "shots": [
            scene(NEO_DESC, "Angeil",
                  "Canon EOS R5", "85mm f/1.4",
                  "Maldivian overwater pier at golden hour — the Andaman sun low, the water turquoise and refracting upward into blue-green fill.",
                  "Maldives overwater pier: the bungalows stretching to the horizon, the water crystalline, the sky doing everything.",
                  "Neo and Angeil at the end of the pier — both looking out at the open ocean, not at each other, both inside their own heads. The creative retreat at its best."),
            scene(NEO_DESC, "Angeil",
                  "Canon EOS R5", "50mm f/2.0",
                  "Three-quarter front, the golden hour backlight.",
                  "The pier, the water, the distant bungalows.",
                  "Both turning toward each other, mid-conversation — the Maldives the backdrop for what is clearly an important creative exchange."),
            scene(NEO_DESC, "Angeil",
                  "Canon EOS R5", "24mm f/5.6",
                  "Wide — the full Maldivian scene, two figures on a pier.",
                  "The complete Maldives — the pier, the water, the bungalows, the horizon.",
                  "Wide — Neo and Angeil small against the enormous Maldivian seascape. Small in the best way. The best creative retreat has the best backdrop."),
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


def build_assets(carousel: dict) -> list:
    partner = carousel["partner"]
    assets = [
        {"path": str(NEO_HERO), "label": "Main Character: Neo"},
    ]
    for ref_path in FRIEND_REFS.get(partner, []):
        if os.path.exists(ref_path):
            label = f"Cast: {partner}"
            assets.append({"path": ref_path, "label": label})

    outfit_path = resolve(carousel.get("outfit", ""))
    if outfit_path and os.path.exists(outfit_path):
        assets.append({"path": outfit_path, "label": "Outfit for Neo (main)"})

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
        caption_path.write_text(carousel["caption"])

        assets = build_assets(carousel)

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
                "image_size": "1K",
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
