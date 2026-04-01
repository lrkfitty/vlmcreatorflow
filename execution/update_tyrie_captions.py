"""
Update Tyrie's caption files with SEO-optimized versions.
Funnel: AI audience → Skool community → CreateFlow subscription.
Run once — rewrites all existing _caption.txt files.
"""
import os
from pathlib import Path

BASE       = Path(__file__).parent.parent
TYRIE_IG   = BASE / "output" / "users" / "Tyrie" / "Instagram"

# Standard hashtag block for every post
HASHTAGS = (
    "#AIContent #AICreator #AIInfluencer #CreateFlow #AIGeneratedContent "
    "#AIMedia #DigitalCreator #ContentCreation #BuildInPublic #AITools "
    "#SkoolCommunity #CreatorEconomy #FutureOfContent #VLM #Bangkok"
)

CTA = "AI-generated content. Built with CreateFlow.\nJoin the community → link in bio."

CAPTIONS = {
    "day01_rooftop_bangkok": f"Built different in a city that never slows down.\n\n{CTA}\n\n{HASHTAGS}",
    "day02_gym_session":     f"The discipline that built the body built the business too.\n\n{CTA}\n\n{HASHTAGS}",
    "day03_night_streets":   f"Every city has a frequency. You either match it or miss it.\n\n{CTA}\n\n{HASHTAGS}",
    "day04_creator_studio":  f"This is where it gets built. No audience required.\n\n{CTA}\n\n{HASHTAGS}",
    "day05_poolside":        f"Recharge so you can go harder when it matters.\n\n{CTA}\n\n{HASHTAGS}",
    "day06_luxury_lobby":    f"Move like you belong everywhere.\n\n{CTA}\n\n{HASHTAGS}",
    "day07_morning_coffee":  f"Mornings are sacred. The silence is part of the work.\n\n{CTA}\n\n{HASHTAGS}",
    "day08_beach_thailand":  f"Culture hits different when you're actually in it.\n\n{CTA}\n\n{HASHTAGS}",
    "day09_penthouse":       f"The bigger the vision, the higher you have to build.\n\n{CTA}\n\n{HASHTAGS}",
    "day10_street_food":     f"Bangkok feeds the body and the soul.\n\n{CTA}\n\n{HASHTAGS}",
    "day11_fine_dining":     f"The best meetings happen over good food.\n\n{CTA}\n\n{HASHTAGS}",
    "day12_temple":          f"Perspective comes from slowing down long enough to look.\n\n{CTA}\n\n{HASHTAGS}",
    "day13_workout_outdoor": f"The body is the foundation. Everything else builds on top.\n\n{CTA}\n\n{HASHTAGS}",
    "day14_skybar":          f"When the city is your backdrop, make it count.\n\n{CTA}\n\n{HASHTAGS}",
    "day15_ai_dashboard":    f"We build the tools so creators don't have to fight the algorithm alone.\n\n{CTA}\n\n{HASHTAGS}",
    "day16_tuk_tuk":         f"Bangkok on your own terms. Always.\n\n{CTA}\n\n{HASHTAGS}",
    "day17_late_night_desk": f"Nobody sees the hours. That's the point.\n\n{CTA}\n\n{HASHTAGS}",
    "day18_riverside":       f"Bangkok has layers. You find new ones every day.\n\n{CTA}\n\n{HASHTAGS}",
    "day19_brand_editorial": f"The brand is the person. Build accordingly.\n\n{CTA}\n\n{HASHTAGS}",
    "day20_co_working":      f"Vision first. The strategy follows.\n\n{CTA}\n\n{HASHTAGS}",
    "day21_sunset_silhouette": f"Some endings set up the best beginnings.\n\n{CTA}\n\n{HASHTAGS}",
    "day22_pool_resort":     f"The reward is part of the system.\n\n{CTA}\n\n{HASHTAGS}",
    "day23_night_portrait":  f"2 AM ideas hit different. Some of them change everything.\n\n{CTA}\n\n{HASHTAGS}",
    "day24_chatuchak":       f"The best ideas come when you stop looking for them.\n\n{CTA}\n\n{HASHTAGS}",
    "day25_presentation":    f"The data tells the story. You just have to be fluent in it.\n\n{CTA}\n\n{HASHTAGS}",
    "day26_morning_run":     f"The city is a track. Use it.\n\n{CTA}\n\n{HASHTAGS}",
    "day27_phone_deal":      f"Every call is a decision. Make them count.\n\n{CTA}\n\n{HASHTAGS}",
    "day28_aerial_city":     f"The city is just a scoreboard. Keep building.\n\n{CTA}\n\n{HASHTAGS}",
    "day29_vip_lounge":      f"The room you're in should match the vision you carry.\n\n{CTA}\n\n{HASHTAGS}",
    "day30_window_reflection": f"30 days. Built in public. Just getting started.\n\n{CTA}\n\n{HASHTAGS}",
}


def run():
    if not TYRIE_IG.exists():
        print(f"Output folder not found: {TYRIE_IG}")
        return

    updated = 0
    for carousel_id, caption in CAPTIONS.items():
        caption_file = TYRIE_IG / f"{carousel_id}_caption.txt"
        caption_file.write_text(caption)
        print(f"Updated: {carousel_id}")
        updated += 1

    print(f"\nDone. {updated} captions updated.")


if __name__ == "__main__":
    run()
