# execution/celebrities.py
# Top 30 Most Famous & Influential People — Visual Description Roster
# Each entry provides a rich prompt description so the model can produce
# a likeness match without depending solely on a celeb's name.

CELEBRITIES = [
    # ── MUSIC ─────────────────────────────────────────────────────────────
    {
        "name": "Beyoncé",
        "category": "Music",
        "gender": "Female",
        "ethnicity": "African American",
        "likeness_hint": 85,
        "prompt_description": (
            "African American woman, honey-blonde long wavy hair, warm brown skin, "
            "almond-shaped brown eyes, high cheekbones, full lips, strong jawline, "
            "statuesque curvaceous figure, commanding presence, radiant complexion"
        ),
    },
    {
        "name": "Taylor Swift",
        "category": "Music",
        "gender": "Female",
        "ethnicity": "Northern European",
        "likeness_hint": 85,
        "prompt_description": (
            "Caucasian woman, light blonde long hair with bangs, fair porcelain skin, "
            "bright blue eyes, heart-shaped face, high cheekbones, red lips, slim athletic figure, "
            "girl-next-door charm meets Hollywood elegance"
        ),
    },
    {
        "name": "Rihanna",
        "category": "Music",
        "gender": "Female",
        "ethnicity": "African American",
        "likeness_hint": 85,
        "prompt_description": (
            "Barbadian woman, dark brown skin, bold almond eyes, strong defined cheekbones, "
            "full lips, slightly wide nose, short cropped or long dark hair (versatile styles), "
            "voluptuous hourglass figure, fearless edgy style"
        ),
    },
    {
        "name": "Drake",
        "category": "Music",
        "gender": "Male",
        "ethnicity": "Mixed Race",
        "likeness_hint": 85,
        "prompt_description": (
            "Mixed-race man (Black and Jewish Canadian), medium-brown skin, close-cropped black hair, "
            "full beard, dark brown eyes, broad forehead, strong jaw, warm smile, "
            "athletic stocky build, relaxed confident demeanor"
        ),
    },
    {
        "name": "The Weeknd",
        "category": "Music",
        "gender": "Male",
        "ethnicity": "African American",
        "likeness_hint": 85,
        "prompt_description": (
            "Ethiopian-Canadian man, dark brown skin, distinctive high-top dreadlocks or closely cropped hair, "
            "intense dark eyes, strong nose, sculpted jaw, slim athletic build, "
            "brooding mysterious expression, sharp modern style"
        ),
    },
    {
        "name": "Cardi B",
        "category": "Music",
        "gender": "Female",
        "ethnicity": "Afro-Latina",
        "likeness_hint": 85,
        "prompt_description": (
            "Afro-Latina woman, bronzed caramel skin, almond-shaped brown eyes, "
            "full sculpted lips, bold arched eyebrows, voluptuous curvaceous figure, "
            "long colorful wigs (various bold colors), expressive animated personality"
        ),
    },

    # ── FILM / TV ─────────────────────────────────────────────────────────
    {
        "name": "Dwayne Johnson",
        "category": "Film/TV",
        "gender": "Male",
        "ethnicity": "Mixed Race",
        "likeness_hint": 85,
        "prompt_description": (
            "Mixed-race man (Black Nova Scotian and Samoan), very dark tan skin, bald head, "
            "wide face, prominent brow ridge, sharp dark eyes, broad wide nose, "
            "massive hyper-muscular physique, 6'5\" towering frame, warm charismatic smile"
        ),
    },
    {
        "name": "Margot Robbie",
        "category": "Film/TV",
        "gender": "Female",
        "ethnicity": "Northern European",
        "likeness_hint": 85,
        "prompt_description": (
            "Australian woman, platinum blonde straight hair, fair skin with light tan, "
            "ice-blue eyes, high defined cheekbones, full lips, petite button nose, "
            "slim athletic figure, effortless glamour, bright infectious smile"
        ),
    },
    {
        "name": "Zendaya",
        "category": "Film/TV",
        "gender": "Female",
        "ethnicity": "Mixed Race",
        "likeness_hint": 85,
        "prompt_description": (
            "Mixed-race woman (African American and European), medium warm-toned skin, "
            "large expressive brown eyes, high sharp cheekbones, full lips, long dark hair "
            "(often long straight or braids), tall slim model-like frame, effortless cool fashion"
        ),
    },
    {
        "name": "Ryan Reynolds",
        "category": "Film/TV",
        "gender": "Male",
        "ethnicity": "Northern European",
        "likeness_hint": 85,
        "prompt_description": (
            "Canadian man, light brown or dirty blonde hair, fair skin, bright blue-green eyes, "
            "strong defined jaw, prominent chin cleft, wide smile with slight smirk, "
            "lean athletic muscular build, charming playful smile"
        ),
    },
    {
        "name": "Kim Kardashian",
        "category": "Film/TV",
        "gender": "Female",
        "ethnicity": "Mixed Race",
        "likeness_hint": 85,
        "prompt_description": (
            "Armenian-American woman, olive warm skin, straight jet-black hair (often sleek), "
            "dark almond eyes under thick defined brows, prominent contoured cheekbones, "
            "full lips, curvaceous hourglass figure, immaculate grooming, glamorous polish"
        ),
    },
    {
        "name": "Denzel Washington",
        "category": "Film/TV",
        "gender": "Male",
        "ethnicity": "African American",
        "likeness_hint": 85,
        "prompt_description": (
            "African American man, dark brown skin, close-cropped salt-and-pepper hair, "
            "deep-set dark eyes under strong brow, broad nose, defined jaw, slight salt-and-pepper stubble, "
            "commanding authoritative presence, tall athletic build, dignified distinguished look"
        ),
    },

    # ── SPORTS ────────────────────────────────────────────────────────────
    {
        "name": "LeBron James",
        "category": "Sports",
        "gender": "Male",
        "ethnicity": "African American",
        "likeness_hint": 85,
        "prompt_description": (
            "African American man, medium dark brown skin, close-cropped black hair (often hairline fade), "
            "dark brown eyes, broad wide nose, wide jaw, 6'9\" enormous athletic muscular frame, "
            "hulking powerful build, intense focused expression"
        ),
    },
    {
        "name": "Cristiano Ronaldo",
        "category": "Sports",
        "gender": "Male",
        "ethnicity": "Mediterranean",
        "likeness_hint": 85,
        "prompt_description": (
            "Portuguese man, olive-tan skin, dark brown styled hair (often slicked or faded sides), "
            "sharp angular jaw, defined chiseled features, dark brown eyes, "
            "extremely lean hyper-muscular athletic physique, confident cocky smile, "
            "prominent veined forearms"
        ),
    },
    {
        "name": "Serena Williams",
        "category": "Sports",
        "gender": "Female",
        "ethnicity": "African American",
        "likeness_hint": 85,
        "prompt_description": (
            "African American woman, dark warm brown skin, long dark hair (straight or braided), "
            "large expressive dark eyes, wide bright smile, strong powerful athletic build, "
            "visibly muscular arms and legs, commanding powerful presence"
        ),
    },
    {
        "name": "Neymar Jr.",
        "category": "Sports",
        "gender": "Male",
        "ethnicity": "Latino/Hispanic",
        "likeness_hint": 85,
        "prompt_description": (
            "Brazilian man, warm light-tan skin, playful colorful or bleached hairstyles (often blonde tips), "
            "dark expressive eyes, wide bright smile, tattoos on arms and body, "
            "slim athletic build, youthful playful energy"
        ),
    },
    {
        "name": "Simone Biles",
        "category": "Sports",
        "gender": "Female",
        "ethnicity": "African American",
        "likeness_hint": 85,
        "prompt_description": (
            "African American woman, warm medium-dark brown skin, petite compact frame (4'8\"), "
            "visibly hyper-muscular athletic build, wide bright smile, dark hair pulled back, "
            "dark expressive eyes, powerful commanding presence despite small stature"
        ),
    },

    # ── BUSINESS / TECH ───────────────────────────────────────────────────
    {
        "name": "Elon Musk",
        "category": "Business/Tech",
        "gender": "Male",
        "ethnicity": "Northern European",
        "likeness_hint": 85,
        "prompt_description": (
            "South African-American man, fair skin, receding light brown hair, "
            "somewhat round face, small dark eyes, broad forehead, heavy-set stocky build, "
            "casual business attire or black t-shirt, intense focused expression, "
            "slight double chin"
        ),
    },
    {
        "name": "Jeff Bezos",
        "category": "Business/Tech",
        "gender": "Male",
        "ethnicity": "Northern European",
        "likeness_hint": 85,
        "prompt_description": (
            "American man, completely bald shaved head, fair skin, warm brown eyes, "
            "wide bright toothy smile, very broad muscular build (visibly fit), "
            "strong defined jaw, confident bold presence"
        ),
    },
    {
        "name": "Oprah Winfrey",
        "category": "Business/Tech",
        "gender": "Female",
        "ethnicity": "African American",
        "likeness_hint": 85,
        "prompt_description": (
            "African American woman, warm dark brown skin, shoulder-length wavy dark hair, "
            "large warm dark eyes, wide warm smile, round face with high cheekbones, "
            "curvy sturdy frame, incredibly warm approachable presence, radiant joy"
        ),
    },
    {
        "name": "Mark Zuckerberg",
        "category": "Business/Tech",
        "gender": "Male",
        "ethnicity": "Northern European",
        "likeness_hint": 85,
        "prompt_description": (
            "American man, fair pale skin, straight dark brown bowl-cut hair, "
            "large round light gray eyes, flat expressionless default look, "
            "thin slim build, plain casual gray t-shirt, slightly robotic stoic demeanor"
        ),
    },

    # ── POLITICS / ROYALS ─────────────────────────────────────────────────
    {
        "name": "Barack Obama",
        "category": "Politics/Royals",
        "gender": "Male",
        "ethnicity": "Mixed Race",
        "likeness_hint": 85,
        "prompt_description": (
            "Mixed-race American man (Kenyan and European), warm medium-brown skin, "
            "close-cropped black salt-and-pepper hair, large prominent ears, "
            "dark expressive eyes, wide warm smile, lean athletic build, "
            "distinguished dignified stature, professorial charisma"
        ),
    },
    {
        "name": "Joe Biden",
        "category": "Politics/Royals",
        "gender": "Male",
        "ethnicity": "Northern European",
        "likeness_hint": 85,
        "prompt_description": (
            "Older American man, white hair, fair skin with age spots, "
            "bright blue eyes, large straight white teeth, slightly hunched posture, "
            "friendly grandfatherly expression, formal suits"
        ),
    },
    {
        "name": "Michelle Obama",
        "category": "Politics/Royals",
        "gender": "Female",
        "ethnicity": "African American",
        "likeness_hint": 85,
        "prompt_description": (
            "African American woman, warm dark brown skin, sleek dark hair (shoulder-length), "
            "warm dark eyes, broad bright smile, strong athletic tall frame, "
            "powerful arms, elegant sophistication, commanding grace"
        ),
    },
    {
        "name": "King Charles III",
        "category": "Politics/Royals",
        "gender": "Male",
        "ethnicity": "Northern European",
        "likeness_hint": 85,
        "prompt_description": (
            "Elderly British man, silver-gray thinning hair, fair ruddy complexion, "
            "large prominent ears, distinguished patrician nose, pale blue eyes, "
            "formal military or suit attire, regal posture"
        ),
    },
    {
        "name": "Taylor Swift (again)" ,  # placeholder slot — see override below
        "category": "placeholder",
        "gender": "Female",
        "ethnicity": "Northern European",
        "likeness_hint": 80,
        "prompt_description": "",
    },  # removed below

    # ── ADDITIONAL ICONS ──────────────────────────────────────────────────
    {
        "name": "Jennifer Lopez",
        "category": "Music",
        "gender": "Female",
        "ethnicity": "Latino/Hispanic",
        "likeness_hint": 85,
        "prompt_description": (
            "Puerto Rican-American woman, warm olive-tan skin, long dark honey-brown hair, "
            "dark almond eyes, full lips, prominent defined cheekbones, "
            "curvy athletic hourglass figure, radiant ageless beauty"
        ),
    },
    {
        "name": "Kendall Jenner",
        "category": "Film/TV",
        "gender": "Female",
        "ethnicity": "Mixed Race",
        "likeness_hint": 85,
        "prompt_description": (
            "American woman, olive skin, long straight dark brown hair, "
            "large dark brown eyes, sharp angular jaw, prominent cheekbones, "
            "tall willowy model figure (5'10\"), cool aloof expression, effortless runway style"
        ),
    },
    {
        "name": "Doja Cat",
        "category": "Music",
        "gender": "Female",
        "ethnicity": "Mixed Race",
        "likeness_hint": 85,
        "prompt_description": (
            "Mixed-race woman (Black and Jewish), warm brown skin, "
            "bold ever-changing hair styles (platinum blonde, shaved, wigs), "
            "large striking brown eyes, defined cheekbones, full lips, "
            "slim figure, avant-garde edgy fashion sense"
        ),
    },
    {
        "name": "Nicki Minaj",
        "category": "Music",
        "gender": "Female",
        "ethnicity": "Mixed Race",
        "likeness_hint": 85,
        "prompt_description": (
            "Trinidadian-American woman, warm caramel skin, bold colorful wigs (pink, blonde, various), "
            "cat-like dark eyes, prominent defined lips, "
            "exaggerated curvaceous figure, extremely bold theatrical style"
        ),
    },
    {
        "name": "Idris Elba",
        "category": "Film/TV",
        "gender": "Male",
        "ethnicity": "African American",
        "likeness_hint": 85,
        "prompt_description": (
            "British-Sierra Leonean man, very dark rich brown skin, "
            "bald or closely shaved head, strong prominent jawline, deep-set dark eyes, "
            "broad nose, tall powerfully built physique, suave commanding presence, "
            "intense smoldering look"
        ),
    },
    {
        "name": "Selena Gomez",
        "category": "Music",
        "gender": "Female",
        "ethnicity": "Latino/Hispanic",
        "likeness_hint": 85,
        "prompt_description": (
            "Mexican-American woman, warm olive skin, long dark brown hair, "
            "large warm brown eyes, naturally thick brows, button nose, "
            "full round face, petite curvy figure, sweet girl-next-door charm"
        ),
    },
    {
        "name": "Elon Musk (duplicate placeholder)",
        "category": "placeholder",
        "gender": "Male",
        "ethnicity": "Northern European",
        "likeness_hint": 80,
        "prompt_description": "",
    },  # removed below
]

# Remove placeholder entries
CELEBRITIES = [c for c in CELEBRITIES if c["category"] != "placeholder"]

# Sorted category list for UI
CELEB_CATEGORIES = sorted(set(c["category"] for c in CELEBRITIES))

def get_celebrities_by_category(category: str = "All") -> list:
    """Returns celebrities filtered by category. 'All' returns all."""
    if category == "All":
        return CELEBRITIES
    return [c for c in CELEBRITIES if c["category"] == category]

def get_celebrity_by_name(name: str):
    """Look up a celebrity by exact name. Returns dict or None."""
    for c in CELEBRITIES:
        if c["name"] == name:
            return c
    return None
