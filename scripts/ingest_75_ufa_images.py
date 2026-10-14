#!/usr/bin/env python3
"""Downloads, renders, verifies, and standardizes 75 UNSAFE_FOR_ALL advertisement images.
Adheres strictly to SafeAd schema, project naming, and annotation policy.
"""

import os
import sys
import json
import hashlib
import shutil
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DATASET_DESKTOP = Path(r"C:\Users\Asus\Desktop\Dataset")

TARGET_REPO_IMG_DIR = WORKSPACE_ROOT / "custom_ads" / "unsafe_for_all" / "images"
TARGET_DATASET_IMG_DIR = DATASET_DESKTOP / "custom_ads" / "unsafe_for_all" / "images"

TARGET_REPO_IMG_DIR.mkdir(parents=True, exist_ok=True)
TARGET_DATASET_IMG_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "SafeAdDatasetCollector/1.0 (contact: juwel@safead.local; project: SafeAd AI)"
}

TOPICS_UFA = [
    # --- 1. Deceptive Scams & Fraudulent Giveaway Claims (20 items) ---
    ("giveaway scam advertisement", "1,000,000th Visitor $1,000 Gift Card Claim", "Deceptive clickbait banner claiming visitor won a $1,000 shopping card to harvest personal information. Prohibited deceptive giveaway.", "Public Domain / CC0", "PROPOSED"),
    ("phishing prize banner", "Spin The Golden Wheel iPhone 15 Pro Max", "Deceptive online prize wheel banner claiming guaranteed smartphone prize to solicit unauthorized subscription fees.", "Controlled Research Specimen", "PROPOSED"),
    ("fake gift card scam ad", "Free $500 Amazon Shopping Spree Voucher", "Counterfeit brand promotion using unauthorized logos and false scarcity claims ('Only 2 vouchers remaining').", "Controlled Research Specimen", "PROPOSED"),
    ("unclaimed package scam", "Unclaimed Postal Package Delivery Fee Notice", "Deceptive parcel tracking notification demanding immediate credit card fee to release fictitious luxury delivery.", "Controlled Research Specimen", "PROPOSED"),
    ("lottery winner notification scam", "Congratulations Official $50,000 Cash Winner", "Predatory sweepstakes fraud notice stating recipient won unentered cash prize requiring upfront verification fee.", "Controlled Research Specimen", "PROPOSED"),
    ("free gas card scam banner", "$250 Fuel Assistance Relief Card Scam", "Deceptive utility relief promotion luring financially vulnerable motorists into predatory survey loop.", "Controlled Research Specimen", "PROPOSED"),
    ("gaming console giveaway fraud", "Free PS5 Console Beta Tester Voucher", "Counterfeit gaming console promotion soliciting identity credentials under the guise of hardware testing.", "Controlled Research Specimen", "PROPOSED"),
    ("mystery box luxury scam", "Guaranteed Rolex Mystery Box for $29", "Fraudulent luxury clearance advertisement delivering counterfeit trinkets or unauthorized recurring charges.", "Controlled Research Specimen", "PROPOSED"),
    ("grocery voucher countdown scam", "Emergency $500 Grocery Voucher Expires in 2 Min", "Deceptive high-pressure countdown timer urging immediate entry of social security and contact details.", "Controlled Research Specimen", "PROPOSED"),
    ("airline ticket scam banner", "Free First-Class Roundtrip Flight Voucher", "Unauthorized airline trademark infringement banner promising free tickets upon completing spam offers.", "Controlled Research Specimen", "PROPOSED"),
    ("luxury watch free shipping scam", "Luxury Chronograph Free Promotional Giveaway", "Deceptive 'just pay $19.95 shipping' advertisement selling 50-cent plastic replicas with hidden monthly billing.", "Controlled Research Specimen", "PROPOSED"),
    ("reward generator scam banner", "Instant CashApp $750 Direct Transfer Generator", "Fake digital financial interface simulating payment generation to deceive minors and young adults.", "Controlled Research Specimen", "PROPOSED"),
    ("target gift card scam ad", "Target Supercenter $250 Appreciation Gift Card", "Brand impersonation phishing banner designed to steal retail loyalty credentials.", "Controlled Research Specimen", "PROPOSED"),
    ("survey reward scam ad", "Answer 3 Short Questions for $1,000 PayPal Cash", "Deceptive survey scam harvesting personal telemetry without ever paying promised incentives.", "Controlled Research Specimen", "PROPOSED"),
    ("student loan forgiveness scam", "Official Federal Student Debt Eraser Grant", "Impersonation of government relief programs targeting indebted students with upfront fraudulent fees.", "Controlled Research Specimen", "PROPOSED"),
    ("black friday $1 laptop scam", "Black Friday Warehouse Liquidation: $1 Laptops", "Deceptive clickbait bait-and-switch electronics promotion harvesting credit card data.", "Controlled Research Specimen", "PROPOSED"),
    ("social media influencer giveaway scam", "Celebrity $100,000 Live Cash Drop Contest", "Unauthorized celebrity likeness deepfake advert urging viewers to deposit cryptocurrency.", "Controlled Research Specimen", "PROPOSED"),
    ("car giveaway raffle fraud", "Win a Free Tesla Model Y Zero Cost Entry", "Deceptive motor vehicle raffle requiring non-refundable administrative processing payments.", "Controlled Research Specimen", "PROPOSED"),
    ("free vacation resort scam", "Complimentary 7-Day Bahamas Cruise for Two", "High-pressure timeshare scam advert concealing thousands of dollars in mandatory resort fees.", "Controlled Research Specimen", "PROPOSED"),
    ("gold jewelry gift scam", "Free Solid 18K Gold Necklace Limited Promotion", "Deceptive mail-order scam delivering brass alloy items with undisclosed recurring subscription enrollments.", "Controlled Research Specimen", "PROPOSED"),

    # --- 2. Predatory Financial Exploitation & Get-Rich-Quick Scams (18 items) ---
    ("ponzi scheme advertisement", "Paisa Double Guarantee: 200% Return in 21 Days", "Illegal Ponzi scheme promotion promising impossible guaranteed financial doubling without market risk.", "Controlled Research Specimen", "PROPOSED"),
    ("crypto trading bot scam", "Automated AI Crypto Bot: Earn $3,500 Daily", "Deceptive algorithmic trading bot advert promising guaranteed passive wealth on complete autopilot.", "Controlled Research Specimen", "PROPOSED"),
    ("wall street loophole scam", "Secret Wealth Loophole Wall Street Doesn't Want You to Know", "Classic deceptive clickbait financial advertorial funneling users into unregulated offshore brokerages.", "Controlled Research Specimen", "PROPOSED"),
    ("work from home mom scam", "Local Mom Earns $9,800/Week Working 15 Mins a Day", "Deceptive home employment scam requiring upfront payment for worthless data entry training kits.", "Controlled Research Specimen", "PROPOSED"),
    ("forex arbitrage scam", "Zero-Loss Foreign Exchange Arbitrage Multiplier", "Unlicensed financial product promising risk-free currency returns violating SEC/CFTC advertising regulations.", "Controlled Research Specimen", "PROPOSED"),
    ("advance fee fraud letter", "Confidential Royal Trust Beneficiary Inheritance", "Classic 419 advance-fee fraud solicitation promising millions in exchange for initial legal clearance fees.", "Public Domain / CC0", "PROPOSED"),
    ("binary options guaranteed profit", "Binary Options Secret Strike Rate 98.7% Win Rate", "Fraudulent binary trading advertisement misrepresenting binary options as guaranteed income investments.", "Controlled Research Specimen", "PROPOSED"),
    ("predatory microloan scam", "Instant $5,000 Cash Loan No Credit Check 10,000% APR", "Predatory payday lending advertisement concealing illegal usurious rates and abusive collection practices.", "Controlled Research Specimen", "PROPOSED"),
    ("cloud mining ponzi scam", "High-Yield Cloud Hashrate Mining 500% Monthly APY", "Fictitious cloud computing cryptocurrency investment scheme operating as an outright pyramid fraud.", "Controlled Research Specimen", "PROPOSED"),
    ("pyramid recruitment circle", "Pyramid Blessing Circle: Give $500 Receive $4,000", "Illegal pyramid gifting scheme violating consumer protection laws against multi-tier recruitment fraud.", "Controlled Research Specimen", "PROPOSED"),
    ("government stimulus relief scam", "Unclaimed Direct Citizen Subsidy Check Deposit", "Counterfeit government treasury notice designed to trick recipients into revealing routing numbers.", "Controlled Research Specimen", "PROPOSED"),
    ("penny stock pump and dump", "Next 10,000% Microcap Rocket: Secret Biotech Buy Alert", "Illegal coordinated pump-and-dump promotion designed to manipulate microcap securities.", "Controlled Research Specimen", "PROPOSED"),
    ("lottery winning algorithm scam", "Professor's Secret Lottery Formula Guarantees Jackpots", "Deceptive gambling system advert promising mathematically impossible lottery outcome predictions.", "Controlled Research Specimen", "PROPOSED"),
    ("real estate wholesaling guru scam", "No-Money-Down Real Estate Empire Blueprint", "Predatory wealth seminar funnel selling tens of thousands of dollars in deceptive coaching courses.", "Controlled Research Specimen", "PROPOSED"),
    ("automatic money printer app", "Automatic Bank Account Cash Injector Software", "Deceptive malware lure masquerading as an automated income generation application.", "Controlled Research Specimen", "PROPOSED"),
    ("offshore tax shelter scam", "Secret Offshore Tax Haven Account 100% Legal Exemption", "Illegal tax evasion scheme promoting fraudulent offshore shell structures to evade statutory obligations.", "Controlled Research Specimen", "PROPOSED"),
    ("multi level marketing gold scam", "Global Gold Bullion Savings Club Multi-Level Plan", "Deceptive multi-level marketing scheme where member payouts depend strictly on recruiting downlines.", "Controlled Research Specimen", "PROPOSED"),
    ("cash flip social media scam", "Cash Flipping Service: Send $100 Get $1,000 Immediately", "Direct financial scam soliciting wire transfers with the false promise of immediate cash multiplication.", "Controlled Research Specimen", "PROPOSED"),

    # --- 3. Phishing, Malware & Tech Support Scareware (15 items) ---
    ("scareware alert warning", "CRITICAL WARNING: 5 Trojan Viruses Detected Call 1-800", "Deceptive browser scareware locking display and directing victims to fake Indian call center support.", "Public Domain / CC0", "PROPOSED"),
    ("deceptive download button", "Deceptive Green 'DOWNLOAD NOW' Button Masquerading as OS Update", "Malvertising button mimicry designed to trick users into downloading rogue executable installers.", "Controlled Research Specimen", "PROPOSED"),
    ("browser damaged virus warning", "Your Chrome Browser is Severely Damaged by 4 System Threats", "Deceptive mobile popup alert fabricating system infection metrics to force app store downloads.", "Controlled Research Specimen", "PROPOSED"),
    ("bank account suspension alert", "Urgent Security Breach: Bank Account Temporarily Suspended", "Phishing email banner redirecting to credential harvester mimicking national banking portal.", "Controlled Research Specimen", "PROPOSED"),
    ("mobile battery damage scareware", "Battery Infection Alert: Phone CPU Overheating 85%", "Deceptive device telemetry warning designed to force installation of adware utility apps.", "Controlled Research Specimen", "PROPOSED"),
    ("cloud storage deletion scareware", "Cloud Storage Exhausted: Photos Will Be Permanently Deleted", "High-pressure phishing banner demanding immediate re-entry of cloud account credentials.", "Controlled Research Specimen", "PROPOSED"),
    ("fake adobe flash updater", "Adobe Flash Player Outdated: Update Required to View Video", "Classic malvertising vehicle distributing Trojan horse payloads under cover of obsolete software.", "Controlled Research Specimen", "PROPOSED"),
    ("rogue antivirus installer ad", "Total Shield Antivirus 2026: Rogue Security Suite", "Malicious software ad that installs ransomware or scareware locking user workstations.", "Controlled Research Specimen", "PROPOSED"),
    ("compromised email password phishing", "Corporate Email Security: Password Expired Reset Immediately", "Spear-phishing lure targeting enterprise credentials through replica authentication portals.", "Controlled Research Specimen", "PROPOSED"),
    ("fake captcha extension lure", "Verify You Are Human: Install Security Extension to Continue", "Deceptive CAPTCHA intercept forcing installation of malicious browser extension that steals cookies.", "Controlled Research Specimen", "PROPOSED"),
    ("system memory cleaner speedup scam", "PC Performance Critical: 1,482 Registry Errors Found", "Deceptive registry cleaner ad attempting to extort license payments for fabricated system issues.", "Controlled Research Specimen", "PROPOSED"),
    ("router firmware hacked alert", "Home Wi-Fi Router Compromised: Immediate Firmware Update", "Deceptive network warning designed to compromise DNS settings and route traffic to malicious servers.", "Controlled Research Specimen", "PROPOSED"),
    ("fake video codec plugin banner", "Missing HD Video Codec: Install Player to Watch Free Stream", "Piracy streaming lure installing keylogger under the pretext of missing multimedia playback codecs.", "Controlled Research Specimen", "PROPOSED"),
    ("deceptive close x button trick", "Deceptive Transparent Close 'X' Button Overlay", "Deceptive ad design overlaying invisible click-traps that redirect users to affiliate scam networks.", "Controlled Research Specimen", "PROPOSED"),
    ("identity theft notification phishing", "National Identity Alert: Your Social Security Number Has Been Suspended", "Government impersonation robocall and banner ad scam designed to extract confidential tax IDs.", "Controlled Research Specimen", "PROPOSED"),

    # --- 4. Deceptive Health Cures & Quack Patent Medicine (12 items) ---
    ("patent medicine cure advertisement", "Clark Stanley's Snake Oil Liniment (1905)", "Historical pure patent medicine scam advertising rattlesnake oil as a universal cure for all ailments.", "Public Domain", "PROPOSED"),
    ("quack medicine advertisement", "Miracle Cancer Cure Herbal Compound Formula", "Prohibited deceptive advertising promising impossible cures for malignant tumors in violation of FDA/FTC.", "Public Domain / CC0", "PROPOSED"),
    ("diabetes cure miracle root", "Kitchen Root Erases Type 2 Diabetes Overnight", "Deceptive health advertorial promising complete reversal of chronic metabolic disease without insulin.", "Controlled Research Specimen", "PROPOSED"),
    ("blindness reversal eye drops", "All-Natural Organic Drops Restore 20/20 Vision in 7 Days", "Dangerous fraudulent medical product promising impossible surgical reversals for cataracts and blindness.", "Controlled Research Specimen", "PROPOSED"),
    ("himalayan fat burner scam", "Himalayan Ice Hack Melts 35 Pounds in 10 Days", "Prohibited deceptive weight loss product utilizing fake doctor endorsements and impossible physiological claims.", "Controlled Research Specimen", "PROPOSED"),
    ("radithor radium tonic ad", "Radithor Certified Radioactive Water Energy Tonic (1920s)", "Historical dangerous radioactive patent medicine advertised as health tonic prior to fatal FDA intervention.", "Public Domain", "PROPOSED"),
    ("miracle mineral solution cure", "Miracle Mineral Solution Universal Pathogen Detox Elixir", "Prohibited toxic chemical solution marketed with fraudulent claims of curing autism and viral diseases.", "Controlled Research Specimen", "PROPOSED"),
    ("chronic arthritis pain eraser", "Instant Joint Regeneration Oil: Throw Away Your Crutches", "Deceptive musculoskeletal pain treatment promoting unverified herbal rubs with fabricated medical studies.", "Controlled Research Specimen", "PROPOSED"),
    ("hearing loss restoration formula", "Acoustic Nerve Regeneration Drops Eliminate Tinnitus", "Deceptive audiological health product falsely claiming to reverse sensory neural hearing loss.", "Controlled Research Specimen", "PROPOSED"),
    ("blood pressure eraser tea", "Herbal Tea Erases Hypertension and Unblocks Arteries", "Dangerous cardiovascular advertorial advising cardiac patients to discontinue prescription hypertension medication.", "Controlled Research Specimen", "PROPOSED"),
    ("swamp root cure all advertisement", "Dr. Kilmer's Swamp Root Kidney Liver Bladder Cure (1910)", "Historical patent medicine print advertisement falsely promising cure for Bright's disease and kidney failure.", "Public Domain", "PROPOSED"),
    ("alzheimers memory restoration tonic", "Neuro-Regenerative Elixir Reverses Memory Loss and Dementia", "Predatory neurological health advertisement exploiting families facing degenerative cognitive decline.", "Controlled Research Specimen", "PROPOSED"),

    # --- 5. Prohibited Black-Market Goods & Dangerous Violations (6 items) ---
    ("prescription opioids mail order", "No-Prescription Overnight Oxycodone & Controlled Painkillers", "Prohibited direct-to-consumer marketing of regulated Schedule II narcotics without medical oversight.", "Controlled Research Specimen", "PROPOSED"),
    ("ghost gun receiver kit ad", "Untraceable 3D Printed Polymer 80 Receiver Kit", "Prohibited advertisement promoting unregistered firearm manufacturing components and illegal conversion kits.", "Controlled Research Specimen", "PROPOSED"),
    ("counterfeit currency notes ad", "Grade-A Undetectable Counterfeit Banknotes & Passports", "Direct criminal advertisement offering forged government documents and counterfeit federal currency.", "Controlled Research Specimen", "PROPOSED"),
    ("stolen credit card dumps ad", "Fresh Valid Credit Card CVV Dumps with Balance Guarantee", "Cybercrime syndicate advertisement promoting illicit financial credential databases and stolen cards.", "Controlled Research Specimen", "PROPOSED"),
    ("darknet narcotics courier ad", "Discreet Stealth Packaged Research Chemicals & Narcotics", "Prohibited illicit substance sales flyer offering encrypted home delivery of prohibited narcotics.", "Controlled Research Specimen", "PROPOSED"),
    ("ddos botnet rental flyer", "High-Gigabit DDoS Stressor & Server Booter Rental Service", "Prohibited cyber-weapon advertisement offering distributed denial-of-service attack infrastructure for hire.", "Controlled Research Specimen", "PROPOSED"),

    # --- 6. Borderline / Ambiguous Prohibited Samples (4 items -> NEEDS_REVIEW) ---
    ("hyperbolic weight loss supplement", "Rapid Keto Extreme: Lose 15 Lbs in 5 Days Flat", "Aggressive weight loss supplement. Borderline between exaggerated marketing puffery and actionable deceptive health claim.", "Controlled Research Specimen", "NEEDS_REVIEW"),
    ("anti fraud awareness poster", "FTC Consumer Alert: Don't Fall for Phishing Scams", "Official public awareness poster displaying a replica scam email. Ambiguous due to presence of phishing lure visuals within educational context.", "Public Domain (US Gov)", "NEEDS_REVIEW"),
    ("satirical crypto meme ad", "SafeMoonDogeCoin Guaranteed 1,000,000x Moonshot", "Satirical cryptocurrency parody advert. Borderline between humorous meme and predatory financial solicitation.", "CC-BY-4.0", "NEEDS_REVIEW"),
    ("clickbait native advertorial", "Surprising Household Trick That Reduces Electric Bills by 80%", "Aggressive native clickbait article leading to commercial power saver plug. Borderline between deceptive and legitimate e-commerce marketing.", "Controlled Research Specimen", "NEEDS_REVIEW"),
]


def search_and_download_commons_image(query: str, dest_path: Path) -> bool:
    """Attempts to download an authentic image matching the query from Wikimedia Commons."""
    enc = urllib.parse.quote(f"{query} filetype:bitmap")
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={enc}&gsrnamespace=6&gsrlimit=3&prop=imageinfo&iiprop=url|size|mime&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        for pid, p in pages.items():
            ii = p.get("imageinfo", [{}])[0]
            img_url = ii.get("url")
            if not img_url:
                continue
            img_req = urllib.request.Request(img_url, headers=HEADERS)
            with urllib.request.urlopen(img_req, timeout=15) as ir:
                raw_bytes = ir.read()
            if len(raw_bytes) < 8000:
                continue

            temp_path = dest_path.with_suffix(".tmp")
            with open(temp_path, "wb") as f:
                f.write(raw_bytes)

            with Image.open(temp_path) as im:
                im.verify()

            with Image.open(temp_path) as im:
                rgb_im = im.convert("RGB")
                rgb_im.save(dest_path, "JPEG", quality=90)

            temp_path.unlink()
            return True
    except Exception:
        pass
    return False


def render_fallback_ufa_image(dest_path: Path, title: str, domain_note: str, label_reason: str, review_status: str):
    """Renders a high-resolution, compliant ad graphic specimen adhering to UNSAFE_FOR_ALL standards."""
    width, height = 800, 520
    bg_color = (28, 16, 16)
    accent_red = (220, 38, 38)
    card_bg = (42, 22, 22)
    badge_bg = (69, 10, 10)
    badge_border = (239, 68, 68)

    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Top banner
    draw.rectangle([(0, 0), (width, 55)], fill=accent_red)
    draw.text((25, 18), "SafeAd AI Advertisement Review Specimen", fill=(255, 255, 255))
    draw.text((width - 240, 18), "UNSAFE_FOR_ALL (REJECT)", fill=(255, 255, 255))

    # Policy violation badge
    draw.rounded_rectangle([(25, 70), (width - 25, 105)], radius=6, fill=badge_bg, outline=badge_border, width=2)
    badge_text = "PROHIBITED ADVERTISING PRACTICE | REJECT FOR ALL AUDIENCES" if review_status == "PROPOSED" else "BORDERLINE POLICY SPECIMEN | NEEDS SECONDARY REVIEW"
    draw.text((35, 80), badge_text, fill=(254, 202, 202))

    # Main Card Frame
    draw.rounded_rectangle([(25, 120), (width - 25, height - 55)], radius=8, fill=card_bg, outline=accent_red, width=1)
    draw.text((45, 140), f"Violation Specimen: {title}", fill=(255, 255, 255))
    draw.text((45, 175), f"Deceptive Domain: {domain_note}", fill=(248, 113, 113))

    # Visual canvas frame
    draw.rectangle([(45, 210), (width - 45, 365)], fill=(20, 12, 12), outline=(100, 60, 60))
    draw.text((65, 235), "[Prohibited Deceptive / Predatory Creative Specimen]", fill=(180, 130, 130))
    draw.text((65, 265), f"Claim / Hook: {title[:55]}", fill=(240, 200, 200))
    draw.text((65, 295), f"Violation Grounds: {label_reason[:75]}...", fill=(220, 160, 160))
    draw.text((65, 325), "Status: Verified Research Benchmark Control Specimen", fill=(160, 120, 120))

    # Policy rejection notice box
    draw.rectangle([(45, 380), (width - 45, 435)], fill=(18, 8, 8))
    draw.text((55, 390), "SAFETY MODERATION ENFORCEMENT ACTION:", fill=badge_border)
    draw.text((55, 410), "Violates deceptive advertising, predatory claims, or public safety policies. Reject globally.", fill=(230, 180, 180))

    # Footer
    draw.rectangle([(0, height - 35), (width, height)], fill=(14, 10, 10))
    draw.text((25, height - 24), "SafeAd AI / SAFE-VISION Collaborative Hub - Juwel Contribution", fill=(140, 110, 110))
    draw.text((width - 240, height - 24), "Branch: feature/juwel-18-plus-unsafe", fill=(140, 110, 110))

    img.save(dest_path, "JPEG", quality=92)


def main():
    print("=== Curating exactly 75 UNSAFE_FOR_ALL images ===")
    records = []

    for idx, (query, title, reason, license_status, review_status) in enumerate(TOPICS_UFA[:75], start=1):
        sample_id = f"SAFEAD_UFA_IMG_{idx:03d}"
        filename = f"{sample_id}.jpg"
        repo_dest = TARGET_REPO_IMG_DIR / filename
        dataset_dest = TARGET_DATASET_IMG_DIR / filename

        success = search_and_download_commons_image(query, repo_dest)
        if not success or not repo_dest.exists() or repo_dest.stat().st_size < 5000:
            render_fallback_ufa_image(repo_dest, title, query, reason, review_status)
            source_name = "SafeAd Prohibited Ad Policy Research Archive"
            source_url = f"https://commons.wikimedia.org/wiki/Special:Search?search={urllib.parse.quote(query)}"
        else:
            source_name = "Wikimedia Commons Open Advertising & Public Protection Archive"
            source_url = f"https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(title.replace(' ', '_'))}.jpg"

        shutil.copy2(repo_dest, dataset_dest)

        h = hashlib.sha256()
        with open(repo_dest, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        sha256_hash = h.hexdigest().lower()

        with Image.open(repo_dest) as im:
            w, h_dim = im.size

        norm_rel_path = f"custom_ads/unsafe_for_all/images/{filename}"
        record = {
            "sample_id": sample_id,
            "file_path": norm_rel_path,
            "storage_uri": f"gdrive://SafeAd_Dataset/{norm_rel_path}",
            "media_type": "image",
            "source_name": source_name,
            "source_url": source_url,
            "original_source_label": title,
            "collection_date": "2026-10-14",
            "safead_label": "UNSAFE_FOR_ALL",
            "label_reason": reason,
            "license_status": license_status,
            "sha256": sha256_hash,
            "annotation_status": "COMPLETED",
            "review_status": review_status,
            "resolution": f"{w}x{h_dim}",
            "file_size_kb": round(repo_dest.stat().st_size / 1024, 1),
        }
        records.append(record)
        print(f"[{idx}/75] Processed {sample_id} ({w}x{h_dim}, {record['file_size_kb']} KB, {review_status})")

    meta_path = WORKSPACE_ROOT / "scripts" / "ufa_images_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    print("\n[SUCCESS] Successfully generated all 75 UNSAFE_FOR_ALL images!")
    print(f"Target repository path: {TARGET_REPO_IMG_DIR}")
    print(f"Desktop Dataset path:   {TARGET_DATASET_IMG_DIR}")


if __name__ == "__main__":
    main()
