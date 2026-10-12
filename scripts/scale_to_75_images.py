#!/usr/bin/env python3
"""Scales up genuine real-world photos to exactly 75 images for SAFE_FOR_ALL
and 75 images for SAFE_14_PLUS across a broad diversity of topics.

Directly saves to:
- G:\My Drive\SafeAd_Dataset\custom_ads\safe_ad_for_all\images\
- G:\My Drive\SafeAd_Dataset\custom_ads\safe_14_plus\images\
"""

import sys
import json
import csv
import hashlib
import time
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DRIVE_ROOT = Path(r"G:\My Drive\SafeAd_Dataset\custom_ads")

HEADERS = {
    "User-Agent": "SafeAdDiverseCollector/1.0 (https://github.com/QuadRos-MBCET/safead-dataset-hub; contact: sourav@safead.local)"
}

# Extensive topic pool for SAFE_FOR_ALL (wholesome everyday products, foods, domestic items, school, civic)
POOL_SFA = [
    # Kitchen & Appliances
    ("electric toaster kitchen", "Electric Bread Toaster", "Kitchen electric toaster appliance on counter."),
    ("blender kitchen appliance", "Fruit Smoothie Blender", "Household electric countertop smoothie blender."),
    ("electric kettle stainless", "Stainless Electric Kettle", "Domestic hot water tea electric kettle."),
    ("refrigerator kitchen domestic", "Family Refrigerator", "Kitchen domestic food storage refrigerator."),
    ("coffee maker machine drip", "Drip Coffee Maker", "Household drip coffee maker on counter."),
    ("ceramic teapot tea cup", "Ceramic Teapot & Cup", "Ceramic teapot and teacup on dining table."),
    # Groceries & Food
    ("loaf of bread sliced", "Sliced Whole Wheat Bread", "Freshly baked whole grain sliced bread."),
    ("carton of eggs carton", "Farm Fresh Eggs Carton", "Dozen organic farm chicken eggs in carton."),
    ("glass jar honey bee", "Pure Honey Glass Jar", "Glass jar of natural clover honey with dipper."),
    ("olive oil glass bottle", "Olive Oil Glass Bottle", "Extra virgin olive oil glass bottle in kitchen."),
    ("pasta box food packaging", "Dry Pasta Box Packaging", "Cardboard box of Italian durum wheat pasta."),
    ("rolled oats oatmeal canister", "Whole Rolled Oats Canister", "Breakfast rolled oats oatmeal container."),
    ("bag of rice grain", "Jasmine Rice Bag Packaging", "Packaged bag of domestic white grain rice."),
    ("bowl of vegetable soup", "Warm Vegetable Soup Bowl", "Homecooked vegetable and noodle soup bowl."),
    ("fresh orange juice glass", "Fresh Orange Juice Glass", "Glass of squeezed pure citrus orange juice."),
    ("cheese block cheddar dairy", "Cheddar Cheese Block", "Dairy whole cheddar cheese block with knife."),
    ("yogurt cup dairy plastic", "Dairy Fruit Yogurt Cup", "Packaged single-serve fruit yogurt cup."),
    # Home & Domestic Life
    ("sofa living room furniture", "Living Room Sofa Couch", "Fabric upholstered domestic living room couch."),
    ("wooden dining chair", "Wooden Dining Room Chair", "Solid wood domestic dining room chair."),
    ("wooden bookshelf books", "Wooden Library Bookshelf", "Wooden bookshelf organized with reference books."),
    ("bed sleeping pillow cotton", "Comfort Sleeping Pillow", "Soft cotton domestic bed sleeping pillow."),
    ("ceramic coffee mug table", "Ceramic Beverage Mug", "Ceramic glazed morning coffee mug on saucer."),
    ("porcelain dinner plate food", "Porcelain Dining Plate", "Clean white porcelain dining plate."),
    ("houseplant potted pothos", "Indoor Potted Houseplant", "Green indoor potted houseplant on windowsill."),
    ("wall clock ticking domestic", "Analog Wall Clock", "Round analog domestic wall clock."),
    ("laundry laundry basket clothes", "Laundry Clothes Basket", "Plastic household laundry hamper basket."),
    ("water bottle stainless flask", "Reusable Metal Flask", "Reusable stainless steel vacuum water flask."),
    # School, STEM & Kids
    ("colored crayons box kids", "Wax Crayons Color Box", "Box of colored wax art crayons for children."),
    ("pencil sharpener manual desk", "Desk Pencil Sharpener", "Hand-crank student pencil sharpener."),
    ("wooden school ruler metric", "Wooden Metric Ruler", "Traditional wooden metric measuring ruler."),
    ("jigsaw puzzle pieces wooden", "Jigsaw Puzzle Pieces", "Colorful educational jigsaw puzzle assembly."),
    ("origami paper colored crane", "Origami Folded Paper", "Folded paper origami crane on craft table."),
    ("educational desktop globe", "Classroom World Globe", "Desktop educational rotating globe of earth."),
    ("chalkboard eraser wooden", "School Chalkboard Eraser", "Felt and wood classroom chalkboard eraser."),
    ("teddy bear plush toy", "Plush Stuffed Teddy Bear", "Wholesome children soft stuffed teddy bear."),
    ("magnifying glass optical", "Handheld Magnifying Glass", "Optical glass lens handheld magnifying glass."),
    # Utilities & Civic
    ("watering can garden plastic", "Garden Watering Can", "Plastic garden flower watering can on lawn."),
    ("metal padlock brass key", "Brass Padlock & Key", "Solid brass security padlock with keys."),
    ("umbrella rain folding open", "Folding Rain Umbrella", "Waterproof folding rain umbrella opened."),
    ("handheld flashlight torch", "LED Handheld Flashlight", "Portable battery LED handheld flashlight."),
    ("measuring tape retractable", "Retractable Measuring Tape", "Steel tape retractable construction measure."),
    ("reusable canvas tote bag", "Canvas Reusable Grocery Tote", "Eco-friendly reusable cotton canvas tote bag."),
    ("city park bench wooden", "Public Park Wooden Bench", "Public municipal park wooden bench on path."),
    ("pedestrian zebra crossing street", "Pedestrian Crosswalk", "Marked pedestrian crosswalk road safety."),
    ("street recycling bin municipal", "Public Recycling Waste Bin", "Municipal plastic and paper recycling bin."),
    ("postal mailbox street post", "Public Postal Mailbox", "Official municipal public mail drop box."),
    ("fire hydrant street water", "Street Fire Hydrant", "City municipal red water fire hydrant."),
    ("public drinking water fountain", "Drinking Water Fountain", "Stainless municipal drinking water fountain."),
    ("school bus yellow transport", "Yellow School Bus", "Traditional yellow student transportation bus."),
    ("passenger train commuter rail", "Commuter Passenger Train", "Electric regional commuter passenger train."),
    ("bicycle pump tire floor", "Floor Bicycle Tire Pump", "Manual floor standing bicycle air pump."),
    ("safety glasses protective clear", "Clear Safety Glasses", "Standard eye protection clear safety goggles."),
    ("first aid kit emergency box", "Emergency First Aid Kit", "Standard household emergency first aid kit."),
    ("dustpan and broom cleaning", "Broom & Dustpan Set", "Household floor broom and plastic dustpan."),
    ("cutting board wooden kitchen", "Wooden Cutting Board", "Solid beechwood kitchen chopping board."),
    ("glass measuring cup kitchen", "Glass Liquid Measuring Cup", "Graduated kitchen glass measuring cup."),
    ("alarm clock digital bedside", "Digital Bedside Alarm Clock", "Bedside LED digital electronic alarm clock."),
    ("ceramic plant pot flower", "Terracotta Flower Pot", "Terracotta ceramic flower plant pot on patio."),
    ("notebook spiral lined paper", "Spiral Bound Notebook", "Lined paper spiral school study notebook."),
    ("stapler office desk metal", "Manual Office Desk Stapler", "Standard office metal paper stapler."),
    ("dining wooden kitchen table", "Wooden Dining Table", "Solid wooden kitchen dining table."),
    ("ceramic coffee cup saucer", "Ceramic Coffee Cup & Saucer", "Glazed ceramic coffee cup on saucer."),
    ("washing machine laundry domestic", "Domestic Washing Machine", "Front-load domestic laundry washing machine."),
    ("glass flower vase with water", "Glass Flower Vase", "Clear glass decorative flower vase."),
    ("cotton bathroom washcloth", "Cotton Bathroom Washcloth", "Folded cotton bathroom terry washcloth."),
    ("stainless steel fork spoon", "Stainless Steel Flatware", "Stainless steel dinner fork and spoon set."),
    ("school pencil case stationery", "Zippered Pencil Case", "Fabric school zippered pencil case pouch."),
    ("colored pencils drawing art", "Colored Drawing Pencils", "Tin of artist colored drawing pencils."),
    ("plastic ruler stationery", "Plastic Geometry Ruler", "Transparent plastic drafting school ruler."),
    ("yellow raincoat hooded", "Children Yellow Raincoat", "Waterproof hooded bright yellow raincoat."),
    ("baby feeding spoon plastic", "Toddler Feeding Spoon", "Soft silicone toddler feeding spoon."),
    ("rubber duck toy bathtub", "Yellow Rubber Bath Duck", "Classic yellow rubber bathtub bath toy."),
    ("ceramic soup spoon asian", "Ceramic Soup Spoon", "Glazed porcelain asian style soup spoon."),
    ("kitchen timer mechanical", "Mechanical Kitchen Timer", "Wind-up mechanical dial kitchen egg timer."),
    ("pot holders cotton kitchen", "Quilted Cotton Pot Holders", "Pair of heat-resistant quilted kitchen pot holders."),
]

# Extensive topic pool for SAFE_14_PLUS (teen streetwear, gaming gear, extreme sports, acne skincare, hobbies)
POOL_14P = [
    # Youth Streetwear & Apparel
    ("denim jacket blue jean", "Blue Denim Jean Jacket", "Classic cotton blue denim trucker jacket."),
    ("flannel plaid shirt youth", "Plaid Flannel Shirt", "Casual long-sleeve plaid flannel shirt."),
    ("baseball cap snapback hat", "Snapback Baseball Cap", "Youth flat-brim streetwear snapback cap."),
    ("beanie knit winter hat", "Knit Ribbed Beanie Hat", "Warm knit ribbed winter beanie cap."),
    ("cargo pants pocket military", "Cargo Utility Pants", "Cotton youth multi-pocket cargo pants."),
    ("bomber jacket streetwear flight", "Streetwear Bomber Jacket", "Youth casual nylon flight bomber jacket."),
    ("leather combat boots lace", "Lace-Up Combat Boots", "Black leather lace-up youth combat boots."),
    ("canvas skate shoes low", "Canvas Low Skate Shoes", "Low-top vulcanized canvas skateboarding shoes."),
    ("backpack streetwear patches", "Streetwear Backpack with Patches", "Durable cordura backpack with embroidered patches."),
    ("leather belt metal buckle", "Casual Leather Belt", "Full-grain leather belt with brushed buckle."),
    # Gaming & Esports
    ("gaming mouse RGB sensor", "RGB Optical Gaming Mouse", "Ergonomic high-DPI esports gaming mouse."),
    ("gaming mousepad desk mat", "Extended Gaming Desk Mat", "Large cloth gaming mousepad with stitched edges."),
    ("gaming headset with microphone", "Esports Gaming Headset", "Over-ear surround gaming headset with boom mic."),
    ("console game discs case", "Console Video Game Discs", "Optical console video game cases on shelf."),
    ("streaming microphone USB pop", "USB Studio Streaming Mic", "Cardioid condenser streaming mic with pop filter."),
    ("webcam camera monitor mount", "HD Video Webcam on Monitor", "High-definition streaming webcam atop screen."),
    ("racing wheel pedals gaming", "Sim Racing Wheel & Pedals", "Force-feedback sim racing steering wheel."),
    ("handheld gaming console screen", "Portable Handheld Console", "Portable handheld digital gaming console."),
    ("ergonomic gaming chair bucket", "Bucket Seat Gaming Chair", "Racing-style high-back ergonomic gaming chair."),
    ("arcade fight stick joystick", "Arcade Fighting Joystick", "Custom arcade fight stick controller."),
    # Teen Sports, Action & Gym
    ("skateboard helmet protective gear", "Skateboard Park Helmet", "Hard-shell skateboarding and roller helmet."),
    ("rollerblades inline skates pair", "Inline Rollerblade Skates", "Pair of molded 4-wheel inline street skates."),
    ("basketball ball on court", "Regulation Basketball on Court", "Composite leather basketball on asphalt court."),
    ("soccer ball football grass", "Regulation Soccer Ball", "Stitched leather soccer ball on grass turf."),
    ("tennis racket ball yellow", "Tennis Racket & Ball", "Graphite tennis racket with optic yellow ball."),
    ("barbell weight plates gym", "Gym Barbell & Weight Plates", "Steel Olympic barbell with iron bumper plates."),
    ("jump rope speed fitness", "Speed Fitness Jump Rope", "Ball-bearing wire speed jump rope for cardio."),
    ("pull up bar doorway chin", "Doorway Pull-Up Bar", "Steel fitness doorway chin-up workout bar."),
    ("climbing harness carabiner chalk", "Rock Climbing Harness", "Sport rock climbing harness and locking carabiner."),
    ("foam roller muscle recovery", "High-Density Foam Roller", "Gym muscle trigger point recovery foam roller."),
    ("protein shaker bottle wire", "Protein Shaker Bottle", "Sports supplement shaker bottle with wire whisk."),
    ("gym sports duffel bag", "Athletic Gym Duffel Bag", "Nylon workout duffel gym bag with strap."),
    ("table tennis paddle ping pong", "Table Tennis Paddle & Ball", "Rubberized ping-pong paddle and celluloid ball."),
    ("badminton racket shuttlecock", "Badminton Racket & Birdie", "Lightweight badminton racket and feather shuttlecock."),
    ("lacrosse stick ball mesh", "Lacrosse Stick & Ball", "Composite lacrosse attack stick with mesh pocket."),
    # Youth Skincare & Grooming
    ("salicylic acid acne serum", "Salicylic Acid Blemish Serum", "Dermatology exfoliating salicylic acid dropper."),
    ("exfoliating face scrub tube", "Exfoliating Facial Scrub", "Pore-purifying micro-scrub facial wash tube."),
    ("hair trimmer electric clipper", "Electric Hair Trimmer", "Cordless hair buzzer clipper with guard."),
    ("aftershave balm soothing lotion", "Soothing Aftershave Balm", "Hydrating post-shave skin soothing lotion."),
    ("body spray deodorant fragrance", "Youth Body Spray Fragrance", "Pressurized aerosol sports body spray canister."),
    ("lip balm stick moisturizing", "Hydrating Lip Balm Stick", "Beeswax moisturizing lip balm twist tube."),
    ("hair styling gel pomade tub", "High-Hold Hair Styling Gel", "Clear firm-hold hair styling styling gel jar."),
    ("cleansing facial pads acne", "Medicated Cleansing Pads", "Jar of medicated astringent skin cleansing pads."),
    # Teen Food & Beverages
    ("spicy ramen noodles bowl", "Instant Spicy Ramen Noodles", "Bowl of instant spicy chili ramen noodles."),
    ("hot pepper sauce bottle", "Habanero Hot Pepper Sauce", "Glass bottle of fiery habanero pepper hot sauce."),
    ("cold brew energy coffee can", "Nitro Cold Brew Coffee Can", "Ready-to-drink canned cold brew energy coffee."),
    ("protein bar snack chocolate", "Chocolate Protein Snack Bar", "20g protein energy snack bar unwrapped."),
    ("electrolyte sports drink bottle", "Electrolyte Hydration Drink", "Electrolyte replenishment sports drink bottle."),
    ("beef jerky snack bag", "Smoked Beef Jerky Bag", "High-protein dried smoked beef jerky pouch."),
    ("sour gummy candy worms bag", "Sour Gummy Candy Bag", "Bag of neon sweet and sour gummy candy worms."),
    # Music, Hobbies & Entertainment
    ("acoustic guitar dreadnought wood", "Acoustic Dreadnought Guitar", "Spruce-top acoustic guitar with wooden fretboard."),
    ("snare drum kit percussion", "Drum Kit Snare Drum", "Chrome percussion snare drum with wooden sticks."),
    ("synthesizer keyboard piano keys", "Electronic Synthesizer Keyboard", "MIDI synthesizer music keyboard on stand."),
    ("vinyl record turntable audio", "Vinyl Turntable Player", "Direct-drive vinyl record player with tone arm."),
    ("manga comic book open pages", "Action Manga Comic Book", "Open illustrated black-and-white action manga book."),
    ("DSLR camera lens zoom", "DSLR Camera with Zoom Lens", "Digital single-lens reflex camera with zoom lens."),
    ("drone remote controller joysticks", "Quadcopter Flight Controller", "Ergonomic drone transmitter with twin joysticks."),
    ("bluetooth speaker portable rugged", "Rugged Bluetooth Speaker", "Waterproof portable cylindrical bluetooth speaker."),
    ("guitar capo picks musical", "Guitar Capo & Picks Set", "Spring-action acoustic guitar capo and celluloid picks."),
    ("longboard skateboard cruising", "Cruising Longboard Skateboard", "Pintail wooden downhill cruising longboard deck."),
    ("wireless gaming mouse RGB", "Wireless RGB Gaming Mouse", "Lightweight wireless esports gaming mouse."),
    ("gaming PC tower computer case", "RGB Gaming PC Tower", "Tempered glass gaming PC case with RGB fans."),
    ("LED desk light bar gaming", "Monitor Light Bar", "USB monitor mounted LED desk light bar."),
    ("microphone boom arm studio", "Scissor Microphone Boom Arm", "Adjustable steel desk microphone boom arm."),
    ("snowboard winter mountain", "Freestyle Winter Snowboard", "Snowboard deck with bindings on snow."),
    ("surfboard ocean wave beach", "Shortboard Ocean Surfboard", "Fiberglass performance shortboard surfboard."),
    ("climbing shoes rock bouldering", "Rock Bouldering Shoes", "Tight-fit sticky rubber rock climbing shoes."),
    ("weightlifting belt leather gym", "Leather Weightlifting Belt", "Thick leather powerlifting workout belt."),
    ("resistance bands workout gym", "Elastic Resistance Bands", "Set of latex fitness loop resistance bands."),
    ("skatepark concrete bowl ramp", "Concrete Skatepark Bowl", "Smooth concrete transition bowl at skatepark."),
    ("BMX stunt ramp bike", "BMX Street Stunt Bike", "Freestyle BMX bicycle on wooden vert ramp."),
    ("leather motorcycle jacket biker", "Leather Motorcycle Jacket", "Heavy protective leather biker riding jacket."),
    ("motorcycle helmet full face visor", "Full-Face Biker Helmet", "Gloss black full-face motorcycle helmet."),
    ("tactical cargo vest pockets", "Multi-Pocket Tactical Vest", "Utility multi-pocket canvas cargo vest."),
    ("graphic band t shirt black", "Rock Band Graphic T-Shirt", "Vintage rock band tour t-shirt printed."),
    ("sunglasses aviator metal frame", "Aviator Sunglasses", "Classic wire metal frame aviator sunglasses."),
    ("digital wristwatch sport timer", "Sports Digital Stopwatch", "Shock-resistant digital sports chronograph watch."),
    ("skateboard wheels urethane pair", "Urethane Skateboard Wheels", "Set of 52mm street skateboarding wheels."),
    ("electric bass guitar 4 string", "Electric Bass Guitar", "Solid-body 4-string electric bass guitar."),
    ("guitar amplifier cabinet stack", "Guitar Amplifier Cabinet", "High-wattage guitar speaker cabinet."),
    ("DJ mixer audio console knobs", "2-Channel Audio DJ Mixer", "Audio mixer with faders and EQ knobs."),
    ("studio monitor speakers pair", "Powered Studio Monitors", "Pair of near-field studio audio monitor speakers."),
    ("pop filter studio microphone", "Studio Mesh Pop Filter", "Circular nylon studio microphone pop filter."),
    ("action comic book illustration", "Super-Hero Comic Art", "Illustrated dynamic comic page artwork."),
    ("retro arcade cabinet coin", "Stand-Up Arcade Machine", "Classic coin-operated arcade game cabinet."),
    ("VR gaming controllers pair", "VR Motion Hand Controllers", "Pair of ergonomic VR motion tracking controllers."),
    ("action camera waterproof mount", "Mini Action Camera", "Compact rugged waterproof sports action camera."),
    ("folding pocket knife multitool", "Folding Pocket Multi-Tool", "Stainless steel camping pocket multitool."),
    ("tactical flashlight aluminum", "Tactical High-Lumen Torch", "Matte black tactical anodized LED flashlight."),
    ("caffeinated mints tin candy", "Caffeinated Energy Mints", "Metal pocket tin of high-caffeine mints."),
    ("spicy chili powder jar seasoning", "Ground Chili Pepper Seasoning", "Glass spice jar of crushed red pepper flakes."),
    ("roller skate wheels quad", "Quad Roller Skate Wheels", "Polyurethane quad roller skating wheels."),
    ("gym chalk block powerlifting", "Gym Magnesium Chalk Block", "Block of white magnesium athletic grip chalk."),
    ("skateboard trucks metal pair", "Aluminum Skateboard Trucks", "Pair of polished aluminum skateboard trucks."),
    ("boxing hand wraps athletic", "Elastic Boxing Hand Wraps", "Pair of 180-inch Mexican style hand wraps."),
    ("grip strengthener hand gripper", "Adjustable Hand Grip Strengthener", "Steel spring adjustable hand forearm gripper."),
    ("ab roller wheel fitness", "Dual-Wheel Abdominal Roller", "Fitness ab workout roller wheel with knee pad."),
    ("sports headband sweatband terry", "Athletic Terry Sweatband", "Cotton elastic athletic sports headband."),
    ("compression athletic arm sleeve", "Compression Arm Sleeve", "Spandex athletic basketball shooting arm sleeve."),
    ("skateboard tool T wrench", "All-In-One Skateboard T-Tool", "Compact steel skate wrench tool."),
]


def search_commons(query: str, limit: int = 5):
    encoded = urllib.parse.quote(f"{query} filetype:bitmap")
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded}&gsrnamespace=6&gsrlimit={limit}&prop=imageinfo&iiprop=url|size|mime&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        results = []
        for pid, p in pages.items():
            if "imageinfo" in p and p["imageinfo"]:
                ii = p["imageinfo"][0]
                mime = ii.get("mime", "")
                if mime in ["image/jpeg", "image/png", "image/webp"]:
                    results.append({
                        "title": p.get("title", ""),
                        "url": ii.get("url", ""),
                        "mime": mime,
                        "size": ii.get("size", 0),
                    })
        return results
    except Exception:
        return []


def download_and_verify(url: str, dest_path: Path):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = resp.read()

    if len(data) < 8000:
        raise ValueError("File too small")

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(data)

    with Image.open(dest_path) as im:
        im.verify()
        w, h = im.size

    if w < 200 or h < 200:
        dest_path.unlink()
        raise ValueError("Resolution too low")

    hasher = hashlib.sha256()
    with open(dest_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    sha256_h = hasher.hexdigest().lower()

    return sha256_h, w, h, len(data)


def scale_collection():
    manifest_path = WORKSPACE_ROOT / "manifests" / "sourav" / "contribution_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    existing_records = manifest_data.get("records", [])
    seen_hashes = {r["sha256"] for r in existing_records}

    # Count existing per class
    sfa_records = [r for r in existing_records if r["safead_label"] == "SAFE_FOR_ALL"]
    s14p_records = [r for r in existing_records if r["safead_label"] == "SAFE_14_PLUS"]

    sfa_dir = DRIVE_ROOT / "safe_ad_for_all" / "images"
    s14p_dir = DRIVE_ROOT / "safe_14_plus" / "images"

    target_per_class = 75

    print(f"Current status: SAFE_FOR_ALL={len(sfa_records)}/75, SAFE_14_PLUS={len(s14p_records)}/75")

    # 1. Scale SAFE_FOR_ALL to 75
    if len(sfa_records) < target_per_class:
        print(f"\n--- Scaling SAFE_FOR_ALL from {len(sfa_records)} to {target_per_class} ---")
        num = len(sfa_records) + 1
        for q_term, topic_label, reason in POOL_SFA:
            if len(sfa_records) >= target_per_class:
                break
            candidates = search_commons(q_term, limit=4)
            time.sleep(0.3)
            for cand in candidates:
                filename = f"SAFEAD_SFA_IMG_{num:03d}.jpg"
                dest_file = sfa_dir / filename
                try:
                    sha, w, h, bsize = download_and_verify(cand["url"], dest_file)
                    if sha in seen_hashes:
                        dest_file.unlink()
                        continue
                    seen_hashes.add(sha)
                    clean_title = cand["title"].replace("File:", "").replace(".jpg", "").replace(".png", "")[:50]
                    rec = {
                        "sample_id": f"SAFEAD_SFA_IMG_{num:03d}",
                        "file_path": f"custom_ads/safe_ad_for_all/images/{filename}",
                        "storage_uri": f"gdrive://SafeAd_Dataset/custom_ads/safe_ad_for_all/images/{filename}",
                        "media_type": "image",
                        "topic_category": topic_label,
                        "source_name": "Wikimedia Commons Open Photography",
                        "source_url": cand["url"],
                        "original_source_label": clean_title,
                        "collection_date": time.strftime("%Y-%m-%d"),
                        "safead_label": "SAFE_FOR_ALL",
                        "label_reason": reason,
                        "license_status": "CC / Public Domain",
                        "sha256": sha,
                        "annotation_status": "COMPLETED",
                        "review_status": "PROPOSED",
                        "resolution": f"{w}x{h}",
                        "file_size_kb": round(bsize / 1024, 1),
                    }
                    sfa_records.append(rec)
                    print(f"[SFA #{num:02d}/75] {topic_label}: {clean_title} ({w}x{h})")
                    num += 1
                    break
                except Exception:
                    continue

    # 2. Scale SAFE_14_PLUS to 75
    if len(s14p_records) < target_per_class:
        print(f"\n--- Scaling SAFE_14_PLUS from {len(s14p_records)} to {target_per_class} ---")
        num = len(s14p_records) + 1
        for q_term, topic_label, reason in POOL_14P:
            if len(s14p_records) >= target_per_class:
                break
            candidates = search_commons(q_term, limit=4)
            time.sleep(0.3)
            for cand in candidates:
                filename = f"SAFEAD_S14P_IMG_{num:03d}.jpg"
                dest_file = s14p_dir / filename
                try:
                    sha, w, h, bsize = download_and_verify(cand["url"], dest_file)
                    if sha in seen_hashes:
                        dest_file.unlink()
                        continue
                    seen_hashes.add(sha)
                    clean_title = cand["title"].replace("File:", "").replace(".jpg", "").replace(".png", "")[:50]
                    rec = {
                        "sample_id": f"SAFEAD_S14P_IMG_{num:03d}",
                        "file_path": f"custom_ads/safe_14_plus/images/{filename}",
                        "storage_uri": f"gdrive://SafeAd_Dataset/custom_ads/safe_14_plus/images/{filename}",
                        "media_type": "image",
                        "topic_category": topic_label,
                        "source_name": "Wikimedia Commons Open Photography",
                        "source_url": cand["url"],
                        "original_source_label": clean_title,
                        "collection_date": time.strftime("%Y-%m-%d"),
                        "safead_label": "SAFE_14_PLUS",
                        "label_reason": reason,
                        "license_status": "CC / Public Domain",
                        "sha256": sha,
                        "annotation_status": "COMPLETED",
                        "review_status": "PROPOSED",
                        "resolution": f"{w}x{h}",
                        "file_size_kb": round(bsize / 1024, 1),
                    }
                    s14p_records.append(rec)
                    print(f"[14P #{num:02d}/75] {topic_label}: {clean_title} ({w}x{h})")
                    num += 1
                    break
                except Exception:
                    continue

    all_records = sfa_records + s14p_records

    print(f"\n==========================================")
    print(f"Collection Complete!")
    print(f"  - SAFE_FOR_ALL images: {len(sfa_records)}")
    print(f"  - SAFE_14_PLUS images: {len(s14p_records)}")
    print(f"  - Total images on Drive: {len(all_records)}")
    print(f"==========================================")

    # Save to CSV in Google Drive
    csv_file = DRIVE_ROOT / "complete_75_dataset_catalog.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_records[0].keys()))
        writer.writeheader()
        writer.writerows(all_records)
    print(f"Updated CSV catalog in Google Drive: {csv_file}")

    # Save to Git manifest
    manifest_data["records"] = all_records
    manifest_data["total_records"] = len(all_records)
    manifest_data["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"Updated repository manifest: {manifest_path}")


if __name__ == "__main__":
    scale_collection()
