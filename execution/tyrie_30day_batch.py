"""
Tyrie + Angeil — 30-Day Instagram Carousel Batch Generator
Personal brand: @tytheguyyttg
Every single shot is a 2-person scene: Tyrie + Angeil, always together.
Master-level photography language in every prompt.
"""
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()
from execution.generate_image import generate_image_from_prompt

BASE = Path(__file__).parent.parent

# ── Character refs ──────────────────────────────────────────────────────────
TYRIE_HERO    = BASE / "assets/AI Content Creators/Friends/Tyrie Master/Tyrie Hero/Tyrie.png"
CLOTHING_DIR  = BASE / "assets/AI Content Creators/Friends/Tyrie Master/Tyrie Clothing"
ANGEIL_HERO   = BASE / "assets/AI Content Creators/Friends/Angeil Master /Angeil Hero image/Angeil.png"
ANGEIL_EXTRAS = BASE / "assets/AI Content Creators/Friends/Black Influencer Models"
ENVS_DIR      = BASE / "assets/AI Content Creators/Environments"
OUTPUT_DIR    = BASE / "output/users/Tyrie/Instagram"

# ── Dynamic outfit pools (all files, rotated by carousel index) ──────────────
def _collect_outfits(directory: Path) -> list:
    exts = {".jpg", ".jpeg", ".png"}
    return sorted([f for f in directory.rglob("*") if f.suffix.lower() in exts and not f.name.startswith("._")])

TYRIE_ALL_OUTFITS  = _collect_outfits(CLOTHING_DIR)

# Angeil uses Shay's massive 148-file library (not her own small 13-file folder)
_SHAY_LIB_2026 = BASE / "assets/AI Content Creators/2026 Jan CLothing "
_SHAY_LIB_INF  = BASE / "assets/AI Content Creators/Influencer CLothing "
def _collect_shay_outfits():
    exts = {".jpg", ".jpeg", ".png"}
    results = []
    for d in [_SHAY_LIB_2026, _SHAY_LIB_INF]:
        results += [f for f in d.rglob("*") if f.suffix.lower() in exts
                    and not f.name.startswith("._")
                    and "Jan 2026 Enviroments" not in str(f)]
    return sorted(results)
ANGEIL_ALL_OUTFITS = _collect_shay_outfits()

# ── Character descriptions ───────────────────────────────────────────────────
TY = (
    "Tall, heavily muscular Black man with full-body tattoos covering both arms, chest, back, and neck. "
    "Athletic physique with defined muscle, short fade haircut, natural authority in every stance. "
    "His tattooed skin catches light and shadow with extraordinary detail. "
    "His presence commands every frame — not posed, but inhabited."
)

ANGEIL = (
    "Beautiful Black woman with melanin-rich skin, modelesque frame, effortless confidence. "
    "Natural or styled hair that shifts by scene and outfit. "
    "She is Ty's partner — there is chemistry between them, not just proximity. "
    "Her glowing brown skin holds highlight and shadow with cinematic depth."
)

COUPLE = f"{TY} {ANGEIL}"

# ── Angeil clothing rotation (12 outfits) ───────────────────────────────────
ANGEIL_OUTFITS = [
    "green fit.jpg",
    "dior dress.jpg",
    "pink two piece .jpg",
    "purple dress .jpg",
    "orange 2 fit.jpg",
    "orange blue jean fit .jpg",
    "bandana ties fit.jpg",
    "brown dainty fit .jpg",
    "tye die .jpg",
    "yellow fit.png",
    "saints lady fit .jpg",
    "white green floral .jpg",
]

# ── 30 carousels ─────────────────────────────────────────────────────────────
CAROUSELS = [
    {
        "id": "day01_rooftop_bangkok",
        "outfit_ty": "Monaco Outfit.jpg",
        "outfit_angeil": "green fit.jpg",
        "env": "Almafi Coast 1.jpg",
        "caption": "Built different in a city that never slows down. She makes every skyline better.\n\n#Bangkok #CreatorLife #VLM #AIEntrepreneur #Createflow",
        "shots": [
            (
                "Canon EOS R5, 85mm f/1.2L wide open at f/1.4. "
                "Late afternoon sun at 22° above horizon, warm backlighting, their faces catching open-shade fill from the reflective Bangkok glass towers. "
                f"{COUPLE} "
                "She stands at the rooftop railing, his tattooed right arm draped loosely across her shoulders — both looking out at the Bangkok skyline panoramic. "
                "Her melanin-rich skin luminous in the amber bounce, his tattoo-covered arms catching directional gold. "
                "Two cocktail glasses sweat on the concrete ledge beside them, the city 40 floors below in creamy bokeh. "
                "Kodak Portra 800 emulation, lifted blacks, warm cast, barely perceptible grain. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 50mm f/2.0. "
                "Three-quarter angle, both turning toward camera — her hand resting on his forearm over her shoulder, slight smile on her face, his jaw relaxed and confident. "
                f"{COUPLE} "
                "Rim light separating them from the background, sky fill warming her cheekbone, his tattooed neck catching the same amber source. "
                "Bangkok skyline glass towers soft in the background at f/2.0. "
                "Chemistry read clearly: partners, not strangers. "
                "Film simulation, warm amber grade, slight vignette. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 24mm f/4 handheld. "
                "Wide rooftop establishing shot — small figures against the massive Bangkok panoramic at golden hour. "
                f"{COUPLE} "
                "She leans back against him, his arms wrapping from behind. Both looking out. City from Silom to Sukhumvit laid out beyond. "
                "Sky gradient from deep orange at the horizon to soft violet above. "
                "Their silhouettes still readable: his athletic outline, her modelesque frame. "
                "Cinematic 2.39:1 crop feel within the 4:5 frame. Warm, saturated. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day02_gym_session",
        "outfit_ty": "Crop vibes fit.png",
        "outfit_angeil": "dior dress.jpg",
        "env": None,
        "caption": "The discipline that built the body built the business too. She watches it all.\n\n#FitLife #Discipline #CreatorLife #Bangkok #VLM",
        "shots": [
            (
                "Sony A1, 70-200mm f/2.8 at 135mm, f/2.8. "
                "Dramatic overhead gym lighting — HMI floods from above, creating sharp definition on muscle and tattoo work. "
                f"{COUPLE} "
                "He stands in front of a gym mirror post-set, arms crossed, tattoos stark under the hard light. She's beside him, hand lightly on his forearm, reflected in the mirror behind. "
                "His melanin-rich tattooed skin holds extraordinary shadow detail under the industrial light. "
                "Her glowing brown skin catches the same hard source with a natural highlight on her cheekbone. "
                "Gym equipment in deep background bokeh. KODAK T-MAX 3200 monochrome emulation then toned warm. Aspect ratio 4:5."
            ),
            (
                "Sony A1, 85mm f/1.4 at f/1.6. "
                "Close-up upper body — her leaning on the pull-up bar beside him, their arms nearly touching, both looking at camera. "
                f"{COUPLE} "
                "His tattooed arm in sharp foreground detail, the ink pattern catching the gym halogen. "
                "Her natural highlight on the collarbone, his muscular definition — the frame is about texture and chemistry. "
                "Shallow depth of field, gym interior soft in the back. "
                "Fuji Eterna Cinema 250D emulation, punchy contrast. Aspect ratio 4:5."
            ),
            (
                "Sony A1, 35mm f/2.8. "
                "Mid-shot — him in motion on the cable machine, she's spotting from behind, watching with intensity. "
                f"{COUPLE} "
                "Motion blur on the weights at 1/60s. His face composed and focused. She's leaning slightly forward, hand ready. "
                "Industrial gym lighting — hard, directional, no fill. "
                "Sweat catching the key light on his tattooed shoulders. Her expression: focused, tuned in. "
                "High-contrast editorial, deep blacks. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day03_night_streets",
        "outfit_ty": "blue Outfit .png",
        "outfit_angeil": "pink two piece .jpg",
        "env": None,
        "caption": "Every city has a frequency. They found it together.\n\n#Bangkok #NightVibes #StreetStyle #CreatorLife",
        "shots": [
            (
                "Leica Q3, 28mm f/1.7. "
                "Bangkok Silom at 11 PM — neon signs in Thai and English reflecting on wet pavement. "
                f"{COUPLE} "
                "Walking side by side, her hand in his tattooed hand, both mid-stride — not posed, genuinely moving through the city. "
                "Neon cyan and magenta spill across his tattoos, warm amber street lamps catching her cheekbone. "
                "A tuk-tuk blurred at 1/15s in the midground, food stall smoke haze in the background. "
                "Street photography grain, slight halation around neon sources. Aspect ratio 4:5."
            ),
            (
                "Leica Q3, 28mm f/2.0. "
                "He's leaning against a Bangkok wall covered in street art — she's facing him, back to camera, hand on his chest. "
                f"{COUPLE} "
                "High contrast — the street art mural lit by a single overhead sodium lamp. His tattoos and the mural compete for visual texture: both win. "
                "Her blonde-adjacent styling catching the warm lamp. His direct eye contact with camera over her shoulder. "
                "Documentary street aesthetic, ISO 6400 grain structure preserved. Aspect ratio 4:5."
            ),
            (
                "Leica Q3, 28mm f/2.8. "
                "Wide intersection shot — both standing at a Bangkok crosswalk while the city churns around them. "
                f"{COUPLE} "
                "They are the still point in a kinetic frame — blurred motorbikes, food carts, pedestrians. "
                "Golden streetlight halo above them, his tattooed silhouette reading strong, her frame elegant beside him. "
                "Long-exposure ambient with flash sync — subjects sharp, world in motion. "
                "Film noir but tropical. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day04_creator_studio",
        "outfit_ty": "green crop fitted .png",
        "outfit_angeil": "purple dress .jpg",
        "env": None,
        "caption": "This is where it gets built. She sees the whole vision.\n\n#BuildInPublic #AIMedia #VLM #Createflow #CreatorStudio",
        "shots": [
            (
                "Canon EOS R5, 35mm f/1.4 at f/1.8. "
                "Dark creative studio — dual monitors showing AI content dashboards, blue and cyan ambient spill. "
                f"{COUPLE} "
                "He is seated at the desk, tattooed forearms on the keyboard, face partially lit by screen. She leans over his shoulder, one hand on the back of his chair, eyes on the screen. "
                "Screen glow illuminating his tattoos with electric blue cast, catching the highlight of her cheekbone in matching tone. "
                "The rest of the room fades to near-black except for a soft purple practitioner light in the far corner. "
                "Cinematic tech aesthetic, ARRI color science emulation. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 85mm f/1.2L at f/1.4. "
                "Close-up detail — his tattooed hands on the keyboard, her hand resting lightly on his forearm at the edge of frame. "
                f"{COUPLE} "
                "Screen glow from below, deep shadow from above. "
                "The tattoo work on his knuckles and forearms in extraordinary detail — fine lines reading against the blue light. "
                "Her brown skin and the edge of her wrist in the corner, the touch deliberate and quiet. "
                "Macro-level intimacy in a tech frame. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 24mm f/2.8. "
                "Wide studio pull-back — full room visible, screens glowing, him at center, she standing a step behind with her arms crossed, watching. "
                f"{COUPLE} "
                "Three monitor setup casting a galaxy of data light across the dark space. "
                "His athletic silhouette and her modelesque form reading clearly against the light sources. "
                "Dramatic and cinematic — the command center of a media company run by two people who built it themselves. "
                "Cyberpunk editorial, cool blue grade. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day05_poolside",
        "outfit_ty": "drip khaki .png",
        "outfit_angeil": "orange 2 fit.jpg",
        "env": "Mint Pool Section Luxury .jpg",
        "caption": "Recharge together. The work is better for it.\n\n#PoolDay #Bangkok #CreatorLife #WorkLifeBalance",
        "shots": [
            (
                "Canon EOS R5, 35mm f/2.0. "
                "Bangkok rooftop infinity pool at golden hour — city skyline beyond the glass edge. "
                f"{COUPLE} "
                "Both seated at the pool edge, feet in the water, his tattooed arm around her waist, she leaning into him. "
                "Late sun at 15° — harsh shadows softened by pool water reflection fill. "
                "Water droplets on his tattooed shoulders catching directional gold. Her orange outfit vivid against the mint-blue water and amber sky. "
                "Travel luxury editorial, Fuji Velvia simulation, saturated and rich. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 85mm f/1.4. "
                "Upper body pool portrait — her back against his chest, both waist-deep in the water. "
                f"{COUPLE} "
                "His tattooed arms wrapped around her from behind, her hands resting over his forearms. "
                "Water droplets and pool shimmer in soft bokeh below frame. "
                "Her glowing brown skin catching the warm afternoon sun on her collarbone, his tattoos reading under refracted pool light. "
                "Chemistry: completely at ease together. Warm, personal, effortless. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 50mm f/4. "
                "Wider shot — both on sun loungers at the pool edge, Bangkok skyline panoramic beyond the infinity edge. "
                f"{COUPLE} "
                "He is reclining on his back, tattoos fully visible from arm to torso. She is sideways on her lounger, leaning toward him, mid-conversation. "
                "Late golden hour shadows long and warm across the terrace. "
                "Two empty glasses on the side table. City haze in the far background. "
                "Lifestyle editorial, warm grade, aspirational. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day06_luxury_lobby",
        "outfit_ty": "ALl saints beige fit.jpg",
        "outfit_angeil": "orange blue jean fit .jpg",
        "env": None,
        "caption": "Move like you belong everywhere. She already does.\n\n#LuxuryLifestyle #Bangkok #CreatorLife #VLM",
        "shots": [
            (
                "Nikon Z9, 35mm f/1.8. "
                "Grand Bangkok hotel lobby — marble floors, towering orchid installation, dramatic pendant lighting. "
                f"{COUPLE} "
                "Walking through together, mid-stride, his hand at the small of her back, both looking forward. Not stopping for the camera — inhabiting the space. "
                "Warm directional downlighting creating oval pools of light on the polished marble. "
                "His tattooed forearm visible where the sleeve ends. Her orange denim outfit commanding color in the cream-and-gold lobby. "
                "Architectural lifestyle editorial. Warm, sharp. Aspect ratio 4:5."
            ),
            (
                "Nikon Z9, 85mm f/1.4. "
                "Lobby portrait — they have stopped near the floral installation, she facing him slightly, he looking at camera. "
                f"{COUPLE} "
                "Pendant light from above creating butterfly lighting on his face, catching her glowing cheekbone in profile. "
                "His tattoos under the warm hotel chandelier light — amber catching every ink line. "
                "The orchids and lobby architecture in soft, creamy bokeh. "
                "Luxury editorial, clean and composed. Aspect ratio 4:5."
            ),
            (
                "Nikon Z9, 24mm f/2.8. "
                "Wide architectural shot — the full lobby scale visible, them small in the grand space but completely owning it. "
                f"{COUPLE} "
                "Marble, gold, glass, and flowers towering above. Their forms at the center leading lines converge toward. "
                "Hotel guests and staff as soft background elements. The architecture frames them as the story. "
                "Grand scale, editorial travel photography, warm and luxurious. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day07_morning_cafe",
        "outfit_ty": "Grren casual fit .jpg",
        "outfit_angeil": "bandana ties fit.jpg",
        "env": None,
        "caption": "Mornings are sacred when you share them right.\n\n#MorningRoutine #CreatorLife #Bangkok #Mindset",
        "shots": [
            (
                "Fujifilm GFX 100S, 63mm f/2.8. "
                "Minimalist Bangkok cafe — floor-to-ceiling windows, warm morning light streaming horizontal across white-washed walls. "
                f"{COUPLE} "
                "Seated across from each other at a small marble table. Two espresso cups between them. She is reading something on her phone, he is watching her with a quiet smile. "
                "Morning window light: golden, directional, soft — the kind that only exists for 20 minutes. Catching her melanin-rich skin with extraordinary warmth, his tattoos in soft side-lit detail. "
                "The scene feels real, not staged: a half-eaten croissant, her bag hooked on the chair. "
                "Kodak Portra 400 emulation, warm and intimate. Aspect ratio 4:5."
            ),
            (
                "Fujifilm GFX 100S, 110mm f/2.0. "
                "Close-up hands — two sets of hands around coffee cups on the marble table, fingertips nearly touching. "
                f"{COUPLE} "
                "His tattooed hands with their rich ink detail, her brown hands with natural shine. "
                "Steam rising from one cup, diffused morning light from the left. "
                "A detail shot that communicates intimacy without showing faces. "
                "Film emulation, lifted shadows, warm cast. Aspect ratio 4:5."
            ),
            (
                "Fujifilm GFX 100S, 45mm f/4. "
                "Wider cafe shot — their table in foreground, Bangkok street life visible through the window behind. "
                f"{COUPLE} "
                "She is laughing at something, head tilted back slightly. He watches her. "
                "Morning cafe ambience: soft murmur of other patrons in background bokeh. "
                "Their ease together — the chemistry of people who do not need to perform. "
                "Lifestyle editorial, soft grain, warm. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day08_beach_thailand",
        "outfit_ty": "drip khaki .png",
        "outfit_angeil": "brown dainty fit .jpg",
        "env": None,
        "caption": "Culture hits different when you're actually in it. Better with her.\n\n#Thailand #IslandLife #Travel #CreatorLife",
        "shots": [
            (
                "Canon EOS R5, 85mm f/1.4. "
                "Thai island beach — white sand, turquoise Andaman water, limestone karsts in the middle distance. "
                f"{COUPLE} "
                "Walking along the shoreline together, bare feet in the shallow wash, his tattooed arm over her shoulders, her arm around his waist. "
                "Hard midday sun softened by a cloud-scatter fill — tattoos vivid, her brown skin luminous. "
                "Sea spray catching the light in foreground. Footprints in the wet sand behind them. "
                "Travel editorial, Fuji Velvia color, rich and saturated. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 50mm f/2.8. "
                "Standing waist-deep in crystal clear water. She is in front of him, facing camera, his hands at her waist. "
                f"{COUPLE} "
                "Water surface refracting light upward — dancing caustics on their skin and his tattoos. "
                "His full tattoo coverage visible from water line to shoulders. "
                "Her dainty outfit wet at the hem, her expression purely happy. "
                "Tropical paradise — pure joy, real moment. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 24mm f/5.6. "
                "Epic wide — small figures on the beach against the dramatic scale of limestone karsts and emerald water. "
                f"{COUPLE} "
                "He is lifting her slightly, both laughing, the karst formation towering 100 meters behind them. "
                "Cinematic scale — the world is enormous and they are perfectly small and happy within it. "
                "Saturated travel photography, sharp foreground, panoramic depth. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day09_penthouse",
        "outfit_ty": "Monaco Outfit.jpg",
        "outfit_angeil": "tye die .jpg",
        "env": None,
        "caption": "The bigger the vision, the higher you have to build.\n\n#VLM #AIEntrepreneur #Bangkok #Vision #Createflow",
        "shots": [
            (
                "Sony A7R V, 35mm f/1.4. "
                "Bangkok penthouse — floor-to-ceiling panoramic windows, the full city skyline from Chao Phraya to Sukhumvit at dusk. "
                f"{COUPLE} "
                "Standing together at the glass, her back against his chest, his hands at her hips — both looking out at the city below. "
                "Ambient city light from outside meeting the warm interior glow. His tattooed arms catching both — warm interior amber on one side, cool city blue on the other. "
                "Her skin glowing in the mixed light. The city laid out before them like a scoreboard. "
                "Cinematic dusk, blue-hour magic. Aspect ratio 4:5."
            ),
            (
                "Sony A7R V, 85mm f/1.4. "
                "Profile at the window — she is facing him, hand pressed lightly to his chest, looking up at him. He looks down at her. "
                f"{COUPLE} "
                "City lights in soft bokeh behind them. His jaw, neck tattoos, and her upturned face catching window light. "
                "The intimacy is quiet: two people who have built something together and know it. "
                "Shallow depth of field, warm cast. Aspect ratio 4:5."
            ),
            (
                "Sony A7R V, 24mm f/2.8. "
                "Wide penthouse interior — the full luxury space visible, them small against the panoramic window. "
                f"{COUPLE} "
                "Designer furniture, low lighting, the city glowing through glass behind them. "
                "Their silhouettes reading as one connected form against the skyline. "
                "Aspirational editorial, deep contrast, blue-hour sky grade. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day10_street_food",
        "outfit_ty": "blue Outfit .png",
        "outfit_angeil": "yellow fit.png",
        "env": None,
        "caption": "Bangkok feeds the body and the soul. She makes it a memory.\n\n#Bangkok #NightMarket #ThaiLife #CreatorLife #Culture",
        "shots": [
            (
                "Leica M11, 35mm f/1.4 Summilux. "
                "Bangkok street food market — glowing stall lanterns, smoke from woks, towers of fresh tropical fruit. "
                f"{COUPLE} "
                "Both at a stall, she holding a bowl of pad thai, he mid-laugh at something she said. "
                "Stall warm orange light falling across his tattoos, catching her yellow outfit and glowing skin. "
                "Smoke haze midground, market crowd in bokeh background. "
                "Candid, warm, real — documentary street photography at its best. Aspect ratio 4:5."
            ),
            (
                "Leica M11, 50mm f/1.4. "
                "Close portrait — her face up close, eyes bright with laughter, bowl of food held up. He is half-frame behind her, grinning. "
                f"{COUPLE} "
                "Warm stall lamplight from one side, a neighbouring stall's neon adding a second color cast. "
                "Her melanin-rich skin glowing in the market warmth. His tattooed arm visible wrapping around her from behind. "
                "Food culture, warmth, genuine delight. Aspect ratio 4:5."
            ),
            (
                "Leica M11, 28mm f/2.8. "
                "Wide market documentary — them moving through the Chatuchak alley together, market on all sides. "
                f"{COUPLE} "
                "She holds his hand, leading slightly, looking back at him laughing. He follows, watching her. "
                "The market alive and vibrant all around: vendors, lanterns, color. "
                "Motion of life, warmth of place, chemistry of two people fully present. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day11_fine_dining",
        "outfit_ty": "Monaco Outfit.jpg",
        "outfit_angeil": "saints lady fit .jpg",
        "env": "Beach Front Restaurant .jpg",
        "caption": "The best meetings happen over good food, with the right person.\n\n#Bangkok #FineDining #Entrepreneur #VLM",
        "shots": [
            (
                "Nikon Z9, 85mm f/1.4 at f/1.8. "
                "Upscale Bangkok beachfront restaurant — candlelight, dark intimate atmosphere, linen napkins, crystal glassware. "
                f"{COUPLE} "
                "Seated across from each other, she has her elbows on the table leaning toward him, he is looking at her, wine glass in tattooed hand. "
                "Candlelight from below — warm flicker catching both their faces, his tattoo ink glowing amber on his forearms. "
                "Her saints lady outfit catching the warm light with luxurious texture. "
                "The ocean visible through the open restaurant side behind them. "
                "Fine dining editorial, warm amber, intimate. Aspect ratio 4:5."
            ),
            (
                "Nikon Z9, 105mm f/2.8. "
                "Detail shot — his tattooed hand holding the wine glass, her hand resting near the centerpiece flowers, both at the table. "
                f"{COUPLE} "
                "The candle flame in sharp focus between their hands. "
                "Tattoo detail extraordinary in the warm candlelight — the flicker revealing ink lines usually lost in flat light. "
                "Luxury lifestyle detail, macro intimacy. Aspect ratio 4:5."
            ),
            (
                "Nikon Z9, 35mm f/2.0. "
                "Wider restaurant shot — their table in center frame, open ocean beyond, soft candles all around. "
                f"{COUPLE} "
                "She's laughing, throwing her head back slightly, he's watching her with quiet satisfaction. "
                "The restaurant beautiful around them — other diners in soft background life. "
                "The kind of night worth remembering: good food, better company. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day12_temple",
        "outfit_ty": "drip khaki .png",
        "outfit_angeil": "white green floral .jpg",
        "env": None,
        "caption": "Perspective comes from slowing down long enough to look. She reminds him to look.\n\n#Bangkok #Thailand #Culture #CreatorLife",
        "shots": [
            (
                "Canon EOS R5, 35mm f/4. "
                "Wat Pho exterior — ancient golden chedi in morning light, monks in saffron in the background distance. "
                f"{COUPLE} "
                "Standing together at the temple base, she looking up at the golden architecture, he watching her reaction. "
                "Sharp morning light at 20° — his tattoos stark in the hard direct sun, her white and green floral dress catching the glow. "
                "The contrast is intentional: heavily tattooed modern man and ancient sacred architecture — she the bridge between them. "
                "Travel editorial, warm and cultural. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 85mm f/2.0. "
                "Profile portrait — both looking toward the temple, her hand in his, his head slightly turned toward her. "
                f"{COUPLE} "
                "Strong morning sidelight. His neck tattoos in relief. Her profile clean and beautiful. "
                "Temple golden detail in warm mid-ground bokeh. "
                "Two people in a rare moment of stillness. Quiet, reverential, real. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 24mm f/5.6. "
                "Wide — small figures at the base of the massive temple complex, golden spires rising above them. "
                f"{COUPLE} "
                "Walking the covered walkway that runs the temple perimeter, ornate pillars framing them repeatedly. "
                "The architectural scale dwarfs them beautifully. "
                "Travel photography at its finest — epic, composed, warm. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day13_outdoor_workout",
        "outfit_ty": "Crop vibes fit.png",
        "outfit_angeil": "orange 2 fit.jpg",
        "env": None,
        "caption": "The body is the foundation. She keeps up.\n\n#FitLife #Bangkok #Discipline #AthleteLife",
        "shots": [
            (
                "Sony A1, 135mm f/1.8. "
                "Bangkok Lumphini Park — sunrise, golden hour mist still low over the grass. "
                f"{COUPLE} "
                "He is in mid-pull-up on the outdoor bar, tattoos and muscle definition sharp in the golden light. She is below, hands on the bar uprights, timing him — competitive and laughing. "
                "Hard sunrise backlight creating rim separation from the misty park behind. "
                "His sweat catching the light, tattoos at maximum definition in the golden angle. "
                "Her orange outfit bright in the warm morning. Athletic energy, genuine effort, real moment. Aspect ratio 4:5."
            ),
            (
                "Sony A1, 85mm f/1.8. "
                "Post-set — him hands on knees, catching breath. She leans against the bar beside him, hand on his sweaty tattooed back. "
                f"{COUPLE} "
                "Hard morning sun from the side, his chest heaving, tattoos sweat-shined and detailed. "
                "Her expression: watching him, somewhere between pride and teasing. "
                "Athletic intimacy — the kind that only exists between two people who push together. "
                "Raw and real. High contrast morning light. Aspect ratio 4:5."
            ),
            (
                "Sony A1, 35mm f/2.8. "
                "Wide park shot — both running on the park track toward camera, Bangkok skyline visible in the morning haze behind. "
                f"{COUPLE} "
                "Him slightly ahead, tattoos visible on arms in motion. Her stride elegant. "
                "The city as backdrop to their discipline: Bangkok waking up behind two people already ahead of it. "
                "Dynamic, inspiring, cinematic. Morning golden hour grade. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day14_skybar",
        "outfit_ty": "ALl saints beige fit.jpg",
        "outfit_angeil": "dior dress.jpg",
        "env": None,
        "caption": "When the city is your backdrop, make it count.\n\n#Bangkok #SkyBar #LuxuryLife #VLM #CreatorLife",
        "shots": [
            (
                "Canon EOS R5, 50mm f/1.4. "
                "Bangkok skybar, 61st floor — open-air terrace, city ablaze 300 meters below. "
                f"{COUPLE} "
                "She is at the railing facing out, his arm around her waist from the side, both holding drinks. "
                "Warm bar lighting from behind, city lights from below creating an upward ambient fill — the kind of light that makes skin glow from every angle. "
                "Her Dior dress catching the warm restaurant light. His tattoos under the bar's atmospheric glow. "
                "Two champagne flutes sweating on the glass railing. City vertigo beautiful and alive behind them. "
                "Night editorial, warm-cool dual tone. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 85mm f/1.2L. "
                "Portrait at the bar — she facing camera, he half-turned looking at her. "
                f"{COUPLE} "
                "City lights bokeh behind them — hundreds of lights from pinpoint to soft circle. "
                "Bar lighting from above catching her glowing cheekbone, his jaw and neck tattoos. "
                "She looks directly at camera with absolute confidence. He watches her. "
                "Night luxury portrait, warm, 85mm depth compression. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 24mm f/2.8. "
                "Wide skybar panoramic — them at the railing, the full Bangkok skyline behind, other skybar guests in soft background life. "
                f"{COUPLE} "
                "Both now facing the city, her head resting slightly on his shoulder. "
                "The city: hundreds of towers, elevated highways, the snake of the Chao Phraya lit gold. "
                "Epic, cinematic, aspirational. The view and the couple equal in beauty. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day15_ai_dashboard",
        "outfit_ty": "green crop fitted .png",
        "outfit_angeil": "purple dress .jpg",
        "env": None,
        "caption": "We build the tools so creators don't have to fight the algorithm alone. She's part of the build.\n\n#Createflow #VLM #AIMedia #FutureOfContent",
        "shots": [
            (
                "Canon EOS R5, 85mm f/1.2L. "
                "Dark creative studio — multiple screens displaying content dashboards, creator analytics, AI workflow interfaces. "
                f"{COUPLE} "
                "He stands facing the screens, arms crossed, tattoos lit by the blue-cyan data glow. She is beside him, one hand on his tattooed arm, studying the same screens. "
                "The screens' light source is the only illumination — cool blue and teal washing over their skin and his ink. "
                "His tattoos as data patterns: the visual metaphor is there without stating it. "
                "Cyberpunk editorial, cool grade, cinematic. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 35mm f/1.8. "
                "She is at the keyboard, him leaning over from behind, tattooed hands braced on the desk on either side of her. "
                f"{COUPLE} "
                "Both focused on the screen. Screen glow illuminating her face from the front, his from above at an angle. "
                "The collaboration is real — not decoration but participation. "
                "Tech creator energy, dual-lit, cinematic. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 24mm f/2.8. "
                "Wide dark studio — full setup visible, multiple screens, equipment, the room a creative command center. "
                f"{COUPLE} "
                "He is standing, she is seated, both looking at the main screen. The screens cast the only color in the room. "
                "Their silhouettes reading against the bright screen matrix. "
                "Futuristic, dark, powerful — two people running something real. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day16_tuk_tuk",
        "outfit_ty": "Grren casual fit .jpg",
        "outfit_angeil": "bandana ties fit.jpg",
        "env": None,
        "caption": "Bangkok on your own terms. Always.\n\n#Bangkok #TukTuk #ThaiLife #Travel #CreatorLife",
        "shots": [
            (
                "Fujifilm X-T5, 23mm f/2.0. "
                "Tuk-tuk moving through Bangkok streets — afternoon traffic, golden light through the canopy gaps. "
                f"{COUPLE} "
                "Both in the back of the tuk-tuk, she leaning out the open side laughing, wind catching her bandana-tied outfit. His tattooed arm out the other side, relaxed grin. "
                "Motion blur on the street at 1/30s — the world blurring past as they stay sharp. "
                "Bangkok street life blurring past: temples, markets, taxis. "
                "Analog warmth, Fuji simulation, travel energy. Aspect ratio 4:5."
            ),
            (
                "Fujifilm X-T5, 35mm f/1.4. "
                "Close-up in the tuk-tuk — her head on his tattooed shoulder, both watching the city go by. "
                f"{COUPLE} "
                "Street light patterns from between buildings catching his tattoos in alternating light and shadow at speed. "
                "Her expression: completely at ease. His: calm, content. "
                "The intimacy of two people in their element. Analog, warm, real. Aspect ratio 4:5."
            ),
            (
                "Fujifilm X-T5, 18mm f/4. "
                "Wide street shot from outside — tuk-tuk passing through a vibrant Bangkok intersection, them visible through the open sides. "
                f"{COUPLE} "
                "Both laughing as the tuk-tuk navigates the chaos. The city blazing all around. "
                "Documentary travel photography — life happening fast and beautifully. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day17_late_night_desk",
        "outfit_ty": "Crop vibes fit.png",
        "outfit_angeil": "brown dainty fit .jpg",
        "env": None,
        "caption": "Nobody sees the hours. That's the point.\n\n#NightOwl #CreatorLife #BuildInPublic #VLM #Grind",
        "shots": [
            (
                "Canon EOS R5, 50mm f/1.4. "
                "Late night home studio — desk lamp as sole light source, warm tungsten against the otherwise dark room. "
                f"{COUPLE} "
                "He is at the desk, pen in tattooed hand, notebook open. She is curled on the couch a meter behind him, one lamp over her, awake — keeping him company in the late hours. "
                "His tattooed forearms in dramatic tungsten-shadow from the lamp. Her figure soft in the background light. "
                "The silence of 2 AM and two people comfortable in it together. "
                "Intimate, warm, real. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 85mm f/1.2. "
                "Close-up — his tattooed hand writing in the notebook, pages filled with dense notes. "
                f"{COUPLE} "
                "Her hand with a mug of tea appears at the edge of frame, setting it beside his notebook — an offering. "
                "Lamplight catching the tattoo ink in extraordinary amber detail. "
                "The mug steam rising, the pen mid-stroke. A micro moment of care between them. "
                "Detail intimacy. Analog warmth. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 28mm f/2.0. "
                "Wide room — him at the desk, lamp circle on the notebook, her asleep on the couch behind him. City lights through the window. "
                f"{COUPLE} "
                "The full quiet of the late-night build visible in one frame. "
                "She stayed. The work continues. The city never fully sleeps. "
                "Cinematic domesticity — real and quietly powerful. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day18_riverside",
        "outfit_ty": "blue Outfit .png",
        "outfit_angeil": "green fit.jpg",
        "env": None,
        "caption": "Bangkok has layers. They find new ones together every day.\n\n#Bangkok #ChaoPhraya #CreatorLife #Explore",
        "shots": [
            (
                "Leica Q3, 28mm f/2.0. "
                "Chao Phraya riverfront — temple-lined bank, ferries cutting the river, late afternoon gold. "
                f"{COUPLE} "
                "Walking the riverside promenade together — her in green fit, his blue outfit catching the afternoon sun. Both looking ahead, her hand looped through his tattooed arm. "
                "Hard directional sun at 25° — tattooed arms in full relief, her green catching a warm glow. "
                "Longtail boat blurred on the river behind them. Temple spires in the background. "
                "Travel street documentary, warm and real. Aspect ratio 4:5."
            ),
            (
                "Leica Q3, 50mm f/2.8. "
                "Riverside portrait — leaning on the railing together, both looking out at the river. "
                f"{COUPLE} "
                "His tattooed arms on the railing, she beside him, elbow touching his. "
                "Late afternoon reflections off the river's surface, casting upward dancing light on them. "
                "Water shimmer on skin — her glowing brown, his ink-covered. "
                "Reflective, quiet, beautiful. Aspect ratio 4:5."
            ),
            (
                "Leica Q3, 28mm f/4. "
                "Wide riverfront establishing — both against the full Bangkok temple skyline on the far bank. "
                f"{COUPLE} "
                "His arm around her shoulder as they face the river scene. Wat Arun's towers lit gold across the water. "
                "Evening ferry passing in mid-ground. River life active and real. "
                "Epic travel composition — people and place in perfect proportion. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day19_brand_editorial",
        "outfit_ty": "Monaco Outfit.jpg",
        "outfit_angeil": "dior dress.jpg",
        "env": None,
        "caption": "The brand is the person. Build accordingly.\n\n#PersonalBrand #CreatorEconomy #VLM #Style #Entrepreneur",
        "shots": [
            (
                "Phase One XT, 110mm f/2.8. "
                "Clean studio — white seamless background, split lighting setup: two large softboxes at 45° each side. "
                f"{COUPLE} "
                "He stands looking directly into the camera, arms at sides. She stands slightly behind him at a 3/4 angle, hand lightly on his tattooed shoulder. "
                "The split lighting reveals every tattoo line with architectural clarity — clean, brand-ready, powerful. "
                "Her Dior dress catching the even studio light with perfect texture. "
                "High fashion commercial, precise and composed. Aspect ratio 4:5."
            ),
            (
                "Phase One XT, 150mm f/2.8. "
                "Close-up editorial portrait — his face direct to camera, neck tattoos in full view. She is in profile behind him, lips near his ear. "
                f"{COUPLE} "
                "Studio Rembrandt light — one main source from above-right creating the triangle on his face, her profile catching matching glow. "
                "Brand campaign quality — the face is the brand. "
                "Technically perfect. Emotionally present. Aspect ratio 4:5."
            ),
            (
                "Phase One XT, 80mm f/5.6. "
                "Full body editorial — both facing camera, slight gap between them, clean studio, full looks visible from crown to heel. "
                f"{COUPLE} "
                "Even studio illumination — every detail of both outfits, every tattoo, every element of their visual identity sharp and readable. "
                "His full tattoo coverage from neck to wrists, her Monaco-level styling. "
                "Commercial campaign final frame — authoritative, aspirational, real. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day20_co_working",
        "outfit_ty": "ALl saints beige fit.jpg",
        "outfit_angeil": "saints lady fit .jpg",
        "env": None,
        "caption": "Vision first. The strategy follows.\n\n#Entrepreneurship #VLM #Createflow #CreatorEconomy #BuildInPublic",
        "shots": [
            (
                "Nikon Z9, 35mm f/1.8. "
                "Modern Bangkok co-working space — floor-to-ceiling windows, city view, warm diffused daylight. "
                f"{COUPLE} "
                "Both standing at the head of a meeting table, he with his hands flat on the table looking at a whiteboard behind him, she beside him pointing at something on the board. "
                "Natural window light from the left — soft and directional. His tattoos in diffused daylight, every line clean. "
                "Her saints lady fit commanding the creative space. "
                "The collaboration is real: two operators building something. Aspect ratio 4:5."
            ),
            (
                "Nikon Z9, 85mm f/1.4. "
                "Seated across the meeting table — she has a laptop open, he is leaning forward elbows on the table listening. "
                f"{COUPLE} "
                "His tattooed forearms on the table, her laptop screen casting secondary light. "
                "Window light softening the scene. Coffee cups between them. "
                "The energy: focused, purposeful. Two people who build things together. Aspect ratio 4:5."
            ),
            (
                "Nikon Z9, 24mm f/2.8. "
                "Wide co-working space — them at the table, Bangkok skyline through the full glass wall behind. "
                f"{COUPLE} "
                "She has stood up, he is looking up at her mid-discussion. The energy is alive. "
                "The full creative space visible — other workers in background life, the city beyond. "
                "The scale of what they're building visible in the architecture around them. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day21_sunset_silhouette",
        "outfit_ty": "green crop fitted .png",
        "outfit_angeil": "orange 2 fit.jpg",
        "env": None,
        "caption": "Some endings set up the best beginnings.\n\n#Bangkok #Sunset #CreatorLife #VLM #Grateful",
        "shots": [
            (
                "Canon EOS R5, 85mm f/8. "
                "Bangkok sunset — sky gradient from orange and deep red at the horizon to violet and deep blue above. "
                f"{COUPLE} "
                "Standing on a rooftop edge together in silhouette — his broad athletic outline with visible tattoo contours, her modelesque frame. "
                "Her hand in his, both facing the sunset. Their silhouettes perfectly distinct but connected. "
                "The sun having just dropped below the skyline, the sky is at peak drama. "
                "Cinematic silhouette, backlit, no fill — pure outline and color. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 200mm f/4. "
                "Semi-silhouette — compressed skyline bringing the distant towers close. Golden half-light on one side of each face. "
                f"{COUPLE} "
                "He is facing the camera, half-lit: one side of his face and tattoos in golden detail, the other in shadow. She faces him in profile, catching the same split. "
                "The Bangkok skyline towers compressed by the 200mm into a wall behind them. "
                "Dramatic, powerful, moody. Golden and shadow equally balanced. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 24mm f/5.6. "
                "Wide golden hour — full Bangkok panoramic in the background, them in the foreground middle-ground. "
                f"{COUPLE} "
                "Her back against his chest, his tattooed arms around her front, looking out together. The entire city visible behind them. "
                "Epic in scale, intimate in detail. "
                "Travel editorial — the city is beautiful but so are they. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day22_resort_pool",
        "outfit_ty": "drip khaki .png",
        "outfit_angeil": "tye die .jpg",
        "env": "Resort Beachfront Pool .jpg",
        "caption": "The reward is part of the system.\n\n#Thailand #Resort #CreatorLife #LuxuryLife #VLM",
        "shots": [
            (
                "Canon EOS R5, 70mm f/2.8. "
                "Luxury Thai resort — jungle pool, private villa in background, midday dappled light through tropical canopy. "
                f"{COUPLE} "
                "He is in the pool, arms on the edge facing out at the jungle. She sits on the pool edge beside him, feet in the water, hand on his tattooed shoulder. "
                "Hard midday sun filtered through canopy — dappled light creating patterns on his tattooed arms and her tye-die outfit. "
                "Pool shimmer casting upward light. Jungle green saturated behind them. "
                "Luxury travel, lush and warm. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 85mm f/1.4. "
                "Pool portrait — she has gotten in too, both at the edge looking out at the jungle view. His tattooed arm around her shoulders. "
                f"{COUPLE} "
                "Water droplets on his tattooed chest and her shoulders in sharp detail. "
                "Jungle beyond in rich green bokeh. Pool water blue-green. "
                "Skin, water, light, tattoos — all in harmony. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 35mm f/4. "
                "Wide resort shot — the full pool and villa landscape visible, them swimming in the foreground. "
                f"{COUPLE} "
                "He is pulling her through the water by her hand, she is laughing. "
                "The resort architecture, jungle canopy, and perfect pool water surrounding the moment. "
                "Travel editorial — luxury, joy, life fully lived. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day23_night_portrait",
        "outfit_ty": "Monaco Outfit.jpg",
        "outfit_angeil": "pink two piece .jpg",
        "env": None,
        "caption": "2 AM ideas hit different. Some change everything.\n\n#NightOwl #CreatorMindset #VLM #BuildingThings",
        "shots": [
            (
                "Canon EOS R5, 85mm f/1.2L at f/1.2. "
                "Night — single phone/screen glow as light source, dark background, intimate frame. "
                f"{COUPLE} "
                "She is holding the phone between them, both looking at it, their faces lit from below in cool blue. "
                "His tattoos catching the screen light with extraordinary detail — the blue light revealing ink that daylight flattens. "
                "Her pink two-piece catching the ambient. Their expressions focused, mid-thought. "
                "Night intimacy, minimal, powerful. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 50mm f/1.4. "
                "His tattooed hand holding a phone, screen light casting blue across the ink. She is at the edge of frame, looking over his shoulder. "
                f"{COUPLE} "
                "The phone as a portal — their window into the world they're building. "
                "Deep blacks, singular light source, precise. "
                "Late-night detail, quiet, cinematic. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 35mm f/2.8. "
                "Both at a window, backs to camera, looking out at the Bangkok night city below. "
                f"{COUPLE} "
                "Her head slightly leaned toward him, his hand on the glass beside hers. "
                "City lights in the dark — millions of lights, hundreds of stories. They can see all of it. "
                "Cinematic rear shot, cool ambient, contemplative and still. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day24_chatuchak",
        "outfit_ty": "Grren casual fit .jpg",
        "outfit_angeil": "yellow fit.png",
        "env": None,
        "caption": "The best ideas come when you stop looking for them.\n\n#Bangkok #Chatuchak #ThaiCulture #CreatorLife",
        "shots": [
            (
                "Fujifilm X100VI, 23mm f/2.0. "
                "Chatuchak Weekend Market — narrow aisles, stalls loaded with art, vintage, crafts, color everywhere. "
                f"{COUPLE} "
                "Both browsing a stall together, her holding up a piece of art, he leaning in to look. Engaged, curious, present. "
                "Dappled shade light — the market covered overhead but open-sided. His tattoos in diffused warm light, her yellow outfit vibrant. "
                "Market life: vendors, color, controlled chaos. Candid, warm, real. Aspect ratio 4:5."
            ),
            (
                "Fujifilm X100VI, 23mm f/1.4. "
                "He is laughing genuinely at something she said, head slightly back. She is grinning, watching his reaction. "
                f"{COUPLE} "
                "Market stall warm-orange lamplight from behind. Both fully in the moment, not performing for anyone. "
                "His face — rare full laugh, tattoos catching the warm market light. Her expression: satisfaction. "
                "Real chemistry, real moment. Analog warmth. Aspect ratio 4:5."
            ),
            (
                "Fujifilm X100VI, 23mm f/4. "
                "Wide market documentary — them navigating the busy Chatuchak lanes together, market life everywhere. "
                f"{COUPLE} "
                "She leads, his tattooed hand in hers, following her into the next aisle. "
                "Color, texture, motion around them. "
                "Life in progress — two people fully in it together. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day25_presentation",
        "outfit_ty": "ALl saints beige fit.jpg",
        "outfit_angeil": "purple dress .jpg",
        "env": None,
        "caption": "The data tells the story. You just have to be fluent in it.\n\n#VLM #Createflow #ContentStrategy #AIMedia #Entrepreneur",
        "shots": [
            (
                "Nikon Z9, 50mm f/1.8. "
                "Modern dark conference room — large presentation screen showing content analytics, him at the front presenting. "
                f"{COUPLE} "
                "He stands pointing at the data on screen, commanding and precise. She is seated at the table in the foreground, notes open, watching with full attention. "
                "Screen light from behind giving him a blue-white edge light. Room ambient low and warm. "
                "His tattooed forearm raised toward the screen, the data behind him. "
                "Her purple dress catching the room's ambient. Power dynamic by choice: presenter and director. Aspect ratio 4:5."
            ),
            (
                "Nikon Z9, 85mm f/1.4. "
                "Close detail — his tattooed hand pointing at a specific metric on the screen. "
                f"{COUPLE} "
                "Her hand with a pen is visible in the foreground, making a note. "
                "The collaboration made physical — both working the same problem from different angles. "
                "Screen light on his tattoo, warm ambient on her wrist. Focus and precision. Aspect ratio 4:5."
            ),
            (
                "Nikon Z9, 24mm f/2.8. "
                "Wide conference room — him at the front, the full screen behind, her and the full table visible. "
                f"{COUPLE} "
                "The boardroom setup: dark walls, one strong screen light, the scale of the operation visible. "
                "Both sharp, both engaged, both building the same thing. "
                "Professional power, together. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day26_morning_run",
        "outfit_ty": "Crop vibes fit.png",
        "outfit_angeil": "orange blue jean fit .jpg",
        "env": None,
        "caption": "The city is a track. Use it.\n\n#MorningRun #Bangkok #FitLife #CreatorLife #Discipline",
        "shots": [
            (
                "Sony A1, 135mm f/1.8. "
                "Bangkok riverside path at sunrise — golden mist over the Chao Phraya, the city waking. "
                f"{COUPLE} "
                "Running side by side toward camera, both in stride, his tattooed arms in full swing, her orange-denim-blue outfit vivid in the morning gold. "
                "Hard sunrise backlight — rim separation from the misty river path behind, their motion sharp against soft bokeh. "
                "Athletic energy, real effort, morning discipline. Golden hour at its peak. Aspect ratio 4:5."
            ),
            (
                "Sony A1, 85mm f/2.0. "
                "They have stopped — he is catching his breath, hands on knees, she is bent forward doing the same. Both in the moment, no performance. "
                f"{COUPLE} "
                "Sweat on his tattooed chest, morning light hard and warm from the side. Her expression: worked hard and earned it. "
                "Bangkok skyline visible in the morning haze behind. "
                "Raw athletic moment, unposed, real. Aspect ratio 4:5."
            ),
            (
                "Sony A1, 35mm f/4. "
                "Wide riverside run path — both small in the distance running toward the city skyline rising from the morning mist. "
                f"{COUPLE} "
                "The river glinting to the left. Temples in the background. Two figures in motion against a city of millions. "
                "Inspiring, cinematic, disciplined. Golden morning grade. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day27_phone_deal",
        "outfit_ty": "blue Outfit .png",
        "outfit_angeil": "white green floral .jpg",
        "env": None,
        "caption": "Every call is a decision. Make them count.\n\n#Entrepreneur #VLM #Createflow #CreatorEconomy #Bangkok",
        "shots": [
            (
                "Fujifilm GFX 50S, 63mm f/2.8. "
                "Large Bangkok cafe window — street visible through glass, morning traffic passing. "
                f"{COUPLE} "
                "He stands at the window on a call, tattooed hand holding phone to ear, deal energy in his posture. She is at the table behind him, laptop open, in her own work zone but glancing at him. "
                "Window light coming from the left — his tattooed arm in sharp sidelight, her white-green floral outfit bright in the secondary light. "
                "The partnership in one frame: two operators, same vision, parallel lanes. Aspect ratio 4:5."
            ),
            (
                "Fujifilm GFX 50S, 110mm f/2.0. "
                "Close-up — his tattooed hand holding the phone, determined expression. Her hand with a coffee mug visible at the edge of frame. "
                f"{COUPLE} "
                "Window light catching the tattoo ink in daylight detail — every line clear. "
                "His expression: focused, direct, negotiating. "
                "The mug at the edge: she's still there. Still in it with him. "
                "Lifestyle detail, sharp and real. Aspect ratio 4:5."
            ),
            (
                "Fujifilm GFX 50S, 45mm f/4. "
                "Wide cafe window shot — him at the glass, full Bangkok street life behind. She visible at her table, watching him with a quiet smile. "
                f"{COUPLE} "
                "The cafe warm and ambient, the street outside busy and real. "
                "His energy charges the room. Her calm is the counterbalance. "
                "Two people in the work, together. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day28_aerial_city",
        "outfit_ty": "green crop fitted .png",
        "outfit_angeil": "green fit.jpg",
        "env": None,
        "caption": "The city is just a scoreboard. Keep building.\n\n#Bangkok #CreatorLife #VLM #Createflow #Vision",
        "shots": [
            (
                "Canon EOS R5, 85mm f/1.4. "
                "High Bangkok rooftop at sunrise — the first rays barely cresting the horizon, the city golden below. "
                f"{COUPLE} "
                "She stands at the rooftop edge, arms spread wide, facing the rising sun. He stands behind her, hands on her shoulders, both facing the new day. "
                "Hard sunrise backlight — rim separating them from the city glow behind. "
                "His tattooed arms catching the very first gold of the day. Her matching green outfit paired with his. "
                "Epic, cinematic, aspirational. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 50mm f/2.0. "
                "Both facing away from camera — looking out at the full Bangkok panoramic, her shoulder against his arm. "
                f"{COUPLE} "
                "His tattoo-covered back fully visible — the entire back piece reading in the morning light. "
                "Her green outfit beside his, the matching intentional. "
                "The city laid out before them: everything they're building it for. "
                "Cinematic rear shot, warm morning, deeply composed. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 24mm f/4. "
                "Wide rooftop — their tiny figures against the full Bangkok panoramic at golden hour. "
                f"{COUPLE} "
                "He has his arm raised, pointing at something on the skyline. She follows his gesture. "
                "The city massive and alive behind them. Their ambition proportional to the scale. "
                "Epic scale, precise detail. This is what it's all for. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day29_vip_lounge",
        "outfit_ty": "Monaco Outfit.jpg",
        "outfit_angeil": "dior dress.jpg",
        "env": None,
        "caption": "The room you're in should match the vision you carry.\n\n#Bangkok #VIPLife #Entrepreneur #NetworkingDoneRight #VLM",
        "shots": [
            (
                "Canon EOS R5, 85mm f/1.4. "
                "Sleek Bangkok VIP lounge — low amber lighting, deep leather seating, curated art on dark walls. "
                f"{COUPLE} "
                "Seated together on a curved leather banquette, he with one arm behind her along the seat back, she leaning slightly toward him. "
                "Warm amber lounge light — his tattoos catching the directional gold, her Dior dress luminous in the glow. "
                "Two drinks on the low table. Music implied by the soft background bokeh of other guests. "
                "Luxury, ease, complete comfort. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 50mm f/1.4. "
                "Portrait at the lounge bar — both looking at camera, he standing with one hand on the bar, she beside him, composed and certain. "
                f"{COUPLE} "
                "Lounge light from above creating the warmest possible portraits — his jaw and neck tattoos in amber detail, her melanin-rich skin luminous. "
                "Confidence reads from both: people who earned the room they're in. "
                "Luxury portrait, warm and precise. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 35mm f/2.0. "
                "Wider lounge shot — them in the foreground, the full exclusive space visible behind. "
                f"{COUPLE} "
                "She is mid-laugh at something he said. He watches her, satisfied. "
                "The lounge: a room full of people who matter, and yet the eye goes to them. "
                "Why? Because they are the most real thing in it. Aspect ratio 4:5."
            ),
        ],
    },
    {
        "id": "day30_window_rain",
        "outfit_ty": "ALl saints beige fit.jpg",
        "outfit_angeil": "brown dainty fit .jpg",
        "env": None,
        "caption": "30 days. Built in public. Just getting started.\n\n#Day30 #CreatorLife #VLM #Createflow #Bangkok #BuildInPublic",
        "shots": [
            (
                "Canon EOS R5, 85mm f/1.2L at f/1.2. "
                "Bangkok apartment at night — heavy rain against the large window, city lights refracting through the water. "
                f"{COUPLE} "
                "Both standing at the rain-streaked window, her cheek against the glass, his tattooed hand pressed beside her face. Both looking out at the dissolving city lights through the rain. "
                "The only light: the city through the rain, fracturing into watercolor behind them. "
                "His tattoos catching the refracted amber and gold. Her brown skin luminous in the same soft glow. "
                "Intimate, cinematic, still. A 30-day bookend. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 50mm f/1.4. "
                "Close detail — his tattooed hand pressed against the rain-streaked glass, city lights behind it like painted bokeh. "
                f"{COUPLE} "
                "Her hand placed over his on the glass — fingers intertwined, the rain between them and the city. "
                "Refracted city lights creating abstract patterns on their hands. "
                "Quiet, symbolic, beautiful. The intimate detail of something real. Aspect ratio 4:5."
            ),
            (
                "Canon EOS R5, 28mm f/2.8. "
                "Wide — their silhouettes at the full window, rain streaming, city a soft blur beyond. "
                f"{COUPLE} "
                "She has her arms wrapped around him from behind, her head against his tattooed back. He faces the window, looking out. "
                "The room dark except for the city's ambient wash through the rain. "
                "The perfect final frame: two people who built something real, still here, still together. Aspect ratio 4:5."
            ),
        ],
    },
]


def build_assets(carousel_idx: int, env=None) -> list:
    """Build the assets list, rotating through ALL outfit files by carousel index."""
    assets = [
        {"path": str(TYRIE_HERO), "label": "Main Character: Tyrie"},
        {"path": str(ANGEIL_HERO), "label": "Cast: Angeil"},
    ]
    # Angeil extra ref
    angeil_eyes = ANGEIL_EXTRAS / "AngeilEyes.JPEG"
    if angeil_eyes.exists():
        assets.append({"path": str(angeil_eyes), "label": "Cast: Angeil (ref 2)"})

    # Rotate through ALL Tyrie outfits
    if TYRIE_ALL_OUTFITS:
        ty_outfit = TYRIE_ALL_OUTFITS[carousel_idx % len(TYRIE_ALL_OUTFITS)]
        assets.append({"path": str(ty_outfit), "label": "Outfit for Main Character"})

    # Rotate through ALL Angeil outfits (offset by half so they don't sync)
    if ANGEIL_ALL_OUTFITS:
        offset = len(ANGEIL_ALL_OUTFITS) // 2
        angeil_outfit = ANGEIL_ALL_OUTFITS[(carousel_idx + offset) % len(ANGEIL_ALL_OUTFITS)]
        assets.append({"path": str(angeil_outfit), "label": "Outfit for Angeil"})

    if env:
        p = ENVS_DIR / env
        if p.exists():
            assets.append({"path": str(p), "label": "Scene Location/Vibe"})

    return assets


def run_batch():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    total = len(CAROUSELS)

    for i, carousel in enumerate(CAROUSELS):
        cid = carousel["id"]
        print(f"\n{'='*60}")
        print(f"[{i+1}/{total}] {cid}")
        print(f"{'='*60}")

        # Write caption with extended CTA
        caption_path = OUTPUT_DIR / f"{cid}_caption.txt"
        ty_cta = (
            "\n\nReal ones move different. Every city, every shot, every move — built with purpose and documented for the record. "
            "This is not content for content's sake. This is legacy.\n\n"
            "Powered by AI. Directed by us. → vlmcreateflow.com 🤖\n"
            "DM for collabs. Link in bio."
        )
        with open(caption_path, "w") as f:
            f.write(carousel["caption"] + ty_cta)

        assets = build_assets(i, carousel.get("env"))

        for j, prompt_text in enumerate(carousel["shots"]):
            shot_num = j + 1
            out_path = OUTPUT_DIR / f"{cid}_shot{shot_num}.jpg"

            if out_path.exists():
                print(f"  [SKIP] shot {shot_num} already exists")
                continue

            print(f"  Generating shot {shot_num}/3...")

            prompt_data = {
                "positive_prompt": prompt_text,
                "aspect_ratio": "4:5",
                "image_size": "4K",
                "assets": assets,
            }

            result = generate_image_from_prompt(prompt_data, output_folder=str(OUTPUT_DIR))

            if result.get("status") == "success" and result.get("image_path"):
                src = Path(result["image_path"])
                if src != out_path and src.exists():
                    import shutil
                    shutil.move(str(src), str(out_path))
                elif src == out_path:
                    pass  # already in right place
                print(f"  Saved: {out_path.name}")

                # Write sidecar meta
                meta = {
                    "carousel_id": cid,
                    "shot_index": j,
                    "cast": ["Tyrie", "Angeil"],
                    "cast_refs": [str(TYRIE_HERO), str(ANGEIL_HERO)],
                    "cast_count": 2,
                    "outfit_ty": carousel.get("outfit_ty", ""),
                    "outfit_angeil": carousel.get("outfit_angeil", ""),
                    "scene_description": carousel.get("env", ""),
                    "prompt_used": prompt_text,
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                }
                meta_path = OUTPUT_DIR / f"{cid}_shot{shot_num}.meta.json"
                with open(meta_path, "w") as mf:
                    json.dump(meta, mf, indent=2)
            else:
                print(f"  FAILED shot {shot_num}: {result.get('logs', '')[:300]}")

            time.sleep(2)

        time.sleep(5)

    print(f"\nDone. {total} carousels (3 shots each) -> {OUTPUT_DIR}")


if __name__ == "__main__":
    run_batch()
