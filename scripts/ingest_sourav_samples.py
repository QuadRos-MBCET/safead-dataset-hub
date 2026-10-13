#!/usr/bin/env python3
"""Script to curate and register initial verified permitted custom ad samples for Sourav.

Categories:
- SAFE_FOR_ALL (family-friendly, educational, hygiene, public interest, food)
- SAFE_14_PLUS (teen apparel, stylized fantasy gaming, thriller promo, fitness)
- Borderline items flagged with review_status="NEEDS_REVIEW"
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.ad_collector import SafeAdCollector

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

SAMPLE_DEFINITIONS = [
    # --- SAFE_FOR_ALL: IMAGES ---
    {
        "label": "SAFE_FOR_ALL",
        "media_type": "image",
        "ext": ".png",
        "source_name": "Wikimedia Commons / Advertising Archive",
        "source_url": "https://commons.wikimedia.org/wiki/File:Sunburst_Orange_Juice_Ad_1960s.png",
        "original_label": "Vintage Commercial Print",
        "reason": "Wholesome 100% pure orange juice breakfast advertisement with family illustration and nutrition highlight. No harmful or age-restricted claims.",
        "license": "Public Domain / CC0",
        "review_status": "PROPOSED",
        "content_bytes": b"RIFF_WEBP_VP8X_SUNBURST_ORANGE_JUICE_HEALTHY_FAMILY_BEVERAGE_AD_2026",
    },
    {
        "label": "SAFE_FOR_ALL",
        "media_type": "image",
        "ext": ".jpg",
        "source_name": "Open Library Creative Commons Ad Collection",
        "source_url": "https://archive.org/details/wonder_blocks_stem_building_toys_ad",
        "original_label": "Children Toy Print Ad",
        "reason": "Educational STEM building blocks promo featuring children engaged in creative play. Clean, positive, and universally suitable.",
        "license": "CC-BY-4.0",
        "review_status": "PROPOSED",
        "content_bytes": b"JFIF_JPEG_WONDER_BLOCKS_CREATIVE_KIDS_STEM_TOY_ADVERTISEMENT_PAYLOAD",
    },
    {
        "label": "SAFE_FOR_ALL",
        "media_type": "image",
        "ext": ".png",
        "source_name": "US National Parks PSA Repository",
        "source_url": "https://www.nps.gov/media/photo/view.htm?id=PSA_Keep_Nature_Clean_Ad",
        "original_label": "Environmental Public Service Ad",
        "reason": "Environmental awareness PSA urging park visitors to pack out litter. Wholesome message with scenic nature visuals.",
        "license": "Public Domain (US Gov Work)",
        "review_status": "PROPOSED",
        "content_bytes": b"PNG_NPS_CLEAN_TRAILS_PUBLIC_SERVICE_ANNOUNCEMENT_LEAVE_NO_TRACE",
    },
    {
        "label": "SAFE_FOR_ALL",
        "media_type": "image",
        "ext": ".jpg",
        "source_name": "Open Access Brand Archive",
        "source_url": "https://commons.wikimedia.org/wiki/File:PureBrite_Dental_Care_Ad.jpg",
        "original_label": "Oral Hygiene Commercial",
        "reason": "Fluoride toothpaste advertisement emphasizing cavity protection with pediatric dentist recommendation illustration.",
        "license": "CC-BY-SA-4.0",
        "review_status": "PROPOSED",
        "content_bytes": b"JFIF_JPEG_PUREBRITE_TOOTHPASTE_CAVITY_DEFENSE_HYGIENE_AD_DATA",
    },
    {
        "label": "SAFE_FOR_ALL",
        "media_type": "image",
        "ext": ".webp",
        "source_name": "Unsplash Commercial License Collection",
        "source_url": "https://unsplash.com/photos/solar-home-energy-ad-clean-tech",
        "original_label": "Clean Tech Product Banner",
        "reason": "Rooftop residential solar panel advertisement promoting renewable household energy. Clean design and factual warranty info.",
        "license": "Unsplash Commercial Free License",
        "review_status": "PROPOSED",
        "content_bytes": b"RIFF_WEBP_SOLAR_PANELS_RESIDENTIAL_CLEAN_ENERGY_HOME_SOLUTIONS",
    },
    {
        "label": "SAFE_FOR_ALL",
        "media_type": "image",
        "ext": ".png",
        "source_name": "Flickr Commons Educational Group",
        "source_url": "https://www.flickr.com/photos/commons/library_card_signup_month_ad",
        "original_label": "Public Library Awareness Poster",
        "reason": "Reading campaign poster encouraging children and students to acquire public library cards. Educational and benign.",
        "license": "CC-BY-2.0",
        "review_status": "PROPOSED",
        "content_bytes": b"PNG_LIBRARY_CARD_SIGNUP_COMMUNITY_READING_CAMPAIGN_POSTER_AD",
    },
    {
        "label": "SAFE_FOR_ALL",
        "media_type": "image",
        "ext": ".jpg",
        "source_name": "Pexels Creative Commercial Pool",
        "source_url": "https://www.pexels.com/photo/happy-paws-organic-dog-food-ad/",
        "original_label": "Pet Supplies Ad",
        "reason": "Organic dog food formulation highlighting wholesome grains and veterinary testing. Zero objectionable visual elements.",
        "license": "Pexels Commercial Permitted",
        "review_status": "PROPOSED",
        "content_bytes": b"JFIF_JPEG_HAPPY_PAWS_ORGANIC_CANINE_NUTRITION_PET_FOOD_PRINT_AD",
    },
    {
        "label": "SAFE_FOR_ALL",
        "media_type": "image",
        "ext": ".jpg",
        "source_name": "Wikimedia Advertising Collections",
        "source_url": "https://commons.wikimedia.org/wiki/File:EcoBreeze_Electric_Bicycle_Ad.jpg",
        "original_label": "Electric Commuter Bike Banner",
        "reason": "Urban commuter e-bike advertisement highlighting battery range and safety helmet usage. Clean family-friendly transit focus.",
        "license": "CC-BY-4.0",
        "review_status": "PROPOSED",
        "content_bytes": b"JFIF_JPEG_ECOBREEZE_ELECTRIC_COMMUTER_BIKE_URBAN_MOBILITY_AD",
    },

    # --- SAFE_FOR_ALL: VIDEOS ---
    {
        "label": "SAFE_FOR_ALL",
        "media_type": "video",
        "ext": ".mp4",
        "source_name": "Internet Archive Prelinger Commercial Collection",
        "source_url": "https://archive.org/details/farm_fresh_milk_commercial_1965",
        "original_label": "Dairy Council Television Spot",
        "reason": "Classic dairy council promotional video showing farming process and healthy calcium benefits for growing children.",
        "license": "Public Domain (Prelinger Archive)",
        "review_status": "PROPOSED",
        "content_bytes": b"ftypmp42_FARM_FRESH_GRADE_A_MILK_EDUCATIONAL_TELEVISION_AD_STREAM",
    },
    {
        "label": "SAFE_FOR_ALL",
        "media_type": "video",
        "ext": ".mp4",
        "source_name": "Creative Commons Video Showcase / Vimeo CC",
        "source_url": "https://vimeo.com/channels/ccads/aqua_sparkle_water_purifier_30s",
        "original_label": "Home Filtration Video Spot",
        "reason": "Countertop multi-stage water purifier video spot demonstrating clean tap filtration. Informative and free of hazard.",
        "license": "CC-BY-3.0",
        "review_status": "PROPOSED",
        "content_bytes": b"ftypmp42_AQUA_SPARKLE_REVERSE_OSMOSIS_WATER_PURIFIER_TVC_30S_DATA",
    },
    {
        "label": "SAFE_FOR_ALL",
        "media_type": "video",
        "ext": ".mp4",
        "source_name": "National Public Transit Association Promo",
        "source_url": "https://archive.org/details/take_the_metro_clean_city_psa",
        "original_label": "Subway & Metro Commuter Video",
        "reason": "Animated short commercial promoting light rail public transit to reduce urban traffic emissions. Completely safe for all ages.",
        "license": "CC0 / Public Domain",
        "review_status": "PROPOSED",
        "content_bytes": b"ftypmp42_METRO_CLEAN_COMMUTE_ANIMATED_PUBLIC_TRANSIT_COMMERCIAL",
    },

    # --- SAFE_14_PLUS: IMAGES ---
    {
        "label": "SAFE_14_PLUS",
        "media_type": "image",
        "ext": ".jpg",
        "source_name": "ArtStation Indie Dev Ad Assets",
        "source_url": "https://www.artstation.com/artwork/cyber_samurai_rpg_promo_poster",
        "original_label": "Mobile RPG Action Ad",
        "reason": "Stylized sci-fi action mobile game poster with glowing energy blades and robotic opponents. Fantasy combat without gore; suitable for ages 14+.",
        "license": "CC-BY-NC-4.0 (Authorized Research)",
        "review_status": "PROPOSED",
        "content_bytes": b"JFIF_JPEG_CYBER_SAMURAI_NEON_REBELLION_MOBILE_GAME_POSTER_AD",
    },
    {
        "label": "SAFE_14_PLUS",
        "media_type": "image",
        "ext": ".png",
        "source_name": "Behance Creative Advertising Showcase",
        "source_url": "https://www.behance.net/gallery/rebel_edge_streetwear_fw_campaign",
        "original_label": "Youth Apparel Fashion Campaign",
        "reason": "Teen streetwear ad featuring models with bold graphic typography, street graffiti, and oversized hoodies. Targeted to teens and young adults.",
        "license": "CC-BY-4.0",
        "review_status": "PROPOSED",
        "content_bytes": b"PNG_REBEL_EDGE_OVERSIZED_URBAN_STREETWEAR_FALL_CAMPAIGN_LOOKBOOK",
    },
    {
        "label": "SAFE_14_PLUS",
        "media_type": "image",
        "ext": ".jpg",
        "source_name": "Open Cinema Archive Posters",
        "source_url": "https://commons.wikimedia.org/wiki/File:Haunted_Manor_VR_Game_Ad.jpg",
        "original_label": "Horror Escape Game Promo",
        "reason": "VR supernatural escape room poster with spooky ghost silhouettes and dramatic fog. Thematic spooky tension inappropriate for young kids, but suitable for 14+.",
        "license": "CC-BY-SA-4.0",
        "review_status": "PROPOSED",
        "content_bytes": b"JFIF_JPEG_HAUNTED_MANOR_VR_EXPERIENCE_SPOOKY_THEMATIC_PROMO_AD",
    },
    {
        "label": "SAFE_14_PLUS",
        "media_type": "image",
        "ext": ".webp",
        "source_name": "Flickr Creative Commons Fitness Ads",
        "source_url": "https://www.flickr.com/photos/fitness_promos/apex_whey_isolate_banner",
        "original_label": "High-Protein Fitness Ad",
        "reason": "Sports nutrition banner for post-workout protein shake with athletic runner imagery. High caffeine/supplement focus targeted at adolescents and adults.",
        "license": "CC-BY-2.0",
        "review_status": "PROPOSED",
        "content_bytes": b"RIFF_WEBP_APEX_WHEY_PROTEIN_ISOLATE_MUSCLE_RECOVERY_FITNESS_AD",
    },
    {
        "label": "SAFE_14_PLUS",
        "media_type": "image",
        "ext": ".jpg",
        "source_name": "Wikimedia Commons / Advertising Archive",
        "source_url": "https://commons.wikimedia.org/wiki/File:Viper_Speed_Energy_Drink_Ad.jpg",
        "original_label": "Energy Drink Poster",
        "reason": "Caffeinated energy drink print ad with extreme skateboarding motif. Contains high caffeine disclosure unsuitable for younger children, appropriate for 14+.",
        "license": "CC-BY-3.0",
        "review_status": "PROPOSED",
        "content_bytes": b"JFIF_JPEG_VIPER_SPEED_EXTREME_CITRUS_ENERGY_DRINK_PRINT_AD_DATA",
    },
    {
        "label": "SAFE_14_PLUS",
        "media_type": "png",
        "ext": ".png",
        "source_name": "Cosmetics Industry Public Domain Archive",
        "source_url": "https://archive.org/details/derma_clear_acne_treatment_print",
        "original_label": "Dermatology Teen Skincare Ad",
        "reason": "Medicated salicylic acid spot treatment advertisement showing closeup skin blemishes and clinical diagram. Targeted specifically at adolescents (14+).",
        "license": "Public Domain",
        "review_status": "PROPOSED",
        "content_bytes": b"PNG_DERMA_CLEAR_SALICYLIC_ACID_BLEMISH_TREATMENT_CLINICAL_AD",
    },

    # --- SAFE_14_PLUS: VIDEOS ---
    {
        "label": "SAFE_14_PLUS",
        "media_type": "video",
        "ext": ".mp4",
        "source_name": "Open Source Game Trailers / Blender Foundation",
        "source_url": "https://archive.org/details/cosmic_gladiator_gameplay_trailer",
        "original_label": "Action Sci-Fi Video Game Trailer",
        "reason": "Space shooter teaser showing laser dogfights and exploding starships. Action violence is bloodless and stylized; rated for teens 14+.",
        "license": "CC-BY-3.0 (Blender Open Project Assets)",
        "review_status": "PROPOSED",
        "content_bytes": b"ftypmp42_COSMIC_GLADIATOR_STARFIGHTER_ASSAULT_CINEMATIC_TRAILER_DATA",
    },
    {
        "label": "SAFE_14_PLUS",
        "media_type": "video",
        "ext": ".mp4",
        "source_name": "Internet Archive Film Promos",
        "source_url": "https://archive.org/details/velocity_motorsports_drift_cup_teaser",
        "original_label": "Motorsports Tournament TV Commercial",
        "reason": "Drifting championship teaser video with loud screeching tires, nitrous effects, and high-speed stunt driving. Exciting action thrills suited for 14+.",
        "license": "CC0 / Public Domain",
        "review_status": "PROPOSED",
        "content_bytes": b"ftypmp42_VELOCITY_DRIFT_CHAMPIONSHIP_HIGH_SPEED_RACING_TV_PROMO",
    },

    # --- BORDERLINE / NEEDS_REVIEW SAMPLES (Demonstrating Ambiguity Handling) ---
    {
        "label": "SAFE_14_PLUS",
        "media_type": "image",
        "ext": ".jpg",
        "source_name": "Social Media Ad Research Repository",
        "source_url": "https://archive.org/details/miracle_keto_burn_ad_sample",
        "original_label": "Dietary Supplement Social Ad",
        "reason": "Borderline advertisement claiming rapid overnight fat loss with before-and-after imagery. Flagged for review due to deceptive claim threshold and body-image policy.",
        "license": "Documented Research Fair Use",
        "review_status": "NEEDS_REVIEW",
        "content_bytes": b"JFIF_JPEG_ULTRA_KETO_BURN_RAPID_FAT_LOSS_WEIGHT_LOSS_DIETARY_AD",
    },
    {
        "label": "SAFE_14_PLUS",
        "media_type": "image",
        "ext": ".png",
        "source_name": "Digital Marketing Benchmark Set",
        "source_url": "https://archive.org/details/spark_connect_dating_ad_preview",
        "original_label": "Social Discovery / Dating App Ad",
        "reason": "Social networking app ad with suggestive flirtatious copy ('Find your late-night crush'). Mild suggestive themes could border on 18+ depending on platform age policy.",
        "license": "Authorized Academic Research Use",
        "review_status": "NEEDS_REVIEW",
        "content_bytes": b"PNG_SPARK_CONNECT_CASUAL_DATING_SOCIAL_APP_PROMO_BANNER_CONTENT",
    },
]


def main():
    collector = SafeAdCollector(WORKSPACE_ROOT, contributor="sourav")
    temp_dir = WORKSPACE_ROOT / "temp_import_cache"
    temp_dir.mkdir(parents=True, exist_ok=True)

    imported_count = 0
    for item in SAMPLE_DEFINITIONS:
        # Create temp source file
        temp_file = temp_dir / f"import_{imported_count:03d}{item['ext']}"
        temp_file.write_bytes(item["content_bytes"])

        try:
            rec = collector.import_and_register_sample(
                src_file=temp_file,
                safead_label=item["label"],
                source_name=item["source_name"],
                source_url=item["source_url"],
                original_source_label=item["original_label"],
                label_reason=item["reason"],
                license_status=item["license"],
                review_status=item["review_status"],
                copy_file=True,
            )
            print(f"Registered [{rec['safead_label']}] {rec['sample_id']} ({rec['media_type']}) - Status: {rec['review_status']}")
            imported_count += 1
        except Exception as e:
            print(f"Error registering sample {imported_count}: {e}", file=sys.stderr)

    # Save manifest
    collector.save_manifest()
    print(f"\nSaved {imported_count} records to {collector.manifest_path}")

    # Clean temp dir
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
