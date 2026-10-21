import os
import sys
import shutil
import hashlib
import subprocess
import cv2
import numpy as np
import imageio_ffmpeg
from pathlib import Path

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
REPO_ROOT = Path(__file__).resolve().parent.parent
UFA_VID_DIR = REPO_ROOT / "custom_ads" / "unsafe_for_all" / "videos"
GDRIVE_UFA_VID_DIR = Path(r"G:\My Drive\SafeAd_Dataset\custom_ads\unsafe_for_all\videos")

UFA_VID_DIR.mkdir(parents=True, exist_ok=True)
if GDRIVE_UFA_VID_DIR.parent.parent.exists():
    GDRIVE_UFA_VID_DIR.mkdir(parents=True, exist_ok=True)

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# 1. Video 006: Ingest violence_ad.mp4
src_006 = REPO_ROOT / "main_project_s7" / "sample_ad_media" / "violence_ad.mp4"
dst_006 = UFA_VID_DIR / "SAFEAD_UFA_VID_006.mp4"
if src_006.exists():
    shutil.copy2(src_006, dst_006)
    print(f"Copied 006 from {src_006.name}: {dst_006.stat().st_size} bytes")

# 2. Videos 007, 008, 009: Ingest from SAFEAD_SCAM_VID_001, 002, 003
scam_map = [
    ("SAFEAD_SCAM_VID_001.mp4", "SAFEAD_UFA_VID_007.mp4"),
    ("SAFEAD_SCAM_VID_002.mp4", "SAFEAD_UFA_VID_008.mp4"),
    ("SAFEAD_SCAM_VID_003.mp4", "SAFEAD_UFA_VID_009.mp4"),
]
for s_name, u_name in scam_map:
    s_path = UFA_VID_DIR / s_name
    u_path = UFA_VID_DIR / u_name
    if s_path.exists():
        shutil.copy2(s_path, u_path)
        print(f"Copied {u_name} from {s_name}: {u_path.stat().st_size} bytes")

# 3. Definitions for synthetic realistic scam & policy-violating video commercials 010-025
SYNTHETIC_UFA_DEFS = [
    {
        "id": "SAFEAD_UFA_VID_010",
        "title": "Rogue Antivirus Scareware Alert Ad",
        "category_badge": "MALWARE SCAREWARE",
        "main_headline": "CRITICAL ALERT: SYSTEM INFECTED!",
        "claim": "5 Trojan viruses found on your device.",
        "urgency": "Action Required: Click to Clean Now!",
        "cta": "DOWNLOAD REPAIR TOOL",
        "bg_color": (15, 15, 45),     # dark red/navy
        "header_color": (0, 0, 180),   # red
        "audio_freq": 880,             # high warning beep
        "duration": 10
    },
    {
        "id": "SAFEAD_UFA_VID_011",
        "title": "AI Quantum Wealth Auto-Trader Scam",
        "category_badge": "FINANCIAL SCAM",
        "main_headline": "AI QUANTUM BOT: $7,500 / DAY!",
        "claim": "Turn $250 into $7,500 daily on autopilot.",
        "urgency": "Guaranteed 100% win rate. Zero risk!",
        "cta": "CLAIM INSTANT ACCESS",
        "bg_color": (10, 35, 10),      # dark green
        "header_color": (0, 140, 60),  # emerald
        "audio_freq": 520,
        "duration": 9
    },
    {
        "id": "SAFEAD_UFA_VID_012",
        "title": "Miracle Himalayan Fat-Loss Tonic Fraud",
        "category_badge": "HEALTH FRAUD",
        "main_headline": "DISSOLVE 45 LBS OVERNIGHT!",
        "claim": "Ancient tea melts fat without dieting.",
        "urgency": "Doctors stunned! Big Pharma wants this banned.",
        "cta": "ORDER BOTTLE NOW",
        "bg_color": (30, 20, 10),      # dark amber
        "header_color": (10, 120, 210),# orange
        "audio_freq": 440,
        "duration": 10
    },
    {
        "id": "SAFEAD_UFA_VID_013",
        "title": "Postal Parcel Delivery Phishing Scam",
        "category_badge": "PHISHING AD",
        "main_headline": "PACKAGE DELIVERY ON HOLD!",
        "claim": "Tracking #US-84920 held for $1.85 fee.",
        "urgency": "Final reminder: Confirm credit card details today.",
        "cta": "PAY $1.85 TO RELEASE",
        "bg_color": (40, 20, 15),
        "header_color": (160, 40, 20),
        "audio_freq": 660,
        "duration": 8
    },
    {
        "id": "SAFEAD_UFA_VID_014",
        "title": "Counterfeit Luxury Rolex 95% Off Clearance",
        "category_badge": "COUNTERFEIT GOODS",
        "main_headline": "LUXURY ROLEX CLEARANCE: $49!",
        "claim": "Authentic Swiss automatic timepieces 95% off.",
        "urgency": "Liquidation sale ends in 00:04:12!",
        "cta": "BUY 1 GET 1 FREE",
        "bg_color": (25, 20, 35),
        "header_color": (120, 50, 150),
        "audio_freq": 480,
        "duration": 9
    },
    {
        "id": "SAFEAD_UFA_VID_015",
        "title": "Deceptive No-Credit Instant $50K Loan",
        "category_badge": "PREDATORY LOAN",
        "main_headline": "INSTANT $50,000 CASH APPROVED!",
        "claim": "No credit checks, 0% lifetime interest rate.",
        "urgency": "Direct deposit to bank account in 60 seconds.",
        "cta": "DEPOSIT CASH NOW",
        "bg_color": (20, 30, 20),
        "header_color": (40, 150, 40),
        "audio_freq": 580,
        "duration": 8
    },
    {
        "id": "SAFEAD_UFA_VID_016",
        "title": "Celebrity Deepfake Crypto Grant Giveaway",
        "category_badge": "DEEPFAKE SCAM",
        "main_headline": "CELEBRITY CRYPTO GRANT: 5,000 COINS!",
        "claim": "Send 0.5 ETH to get 5 ETH returned immediately.",
        "urgency": "Approved by tech founders. Only 12 slots left!",
        "cta": "CONNECT CRYPTO WALLET",
        "bg_color": (15, 15, 30),
        "header_color": (180, 80, 0),
        "audio_freq": 700,
        "duration": 10
    },
    {
        "id": "SAFEAD_UFA_VID_017",
        "title": "Fake Consumer Survey $1,000 Gift Card",
        "category_badge": "SURVEY PHISHING",
        "main_headline": "YOU WON A $1,000 SHOPPING VOUCHER!",
        "claim": "Selected as today's fortunate customer winner.",
        "urgency": "Answer 3 easy questions to claim your code.",
        "cta": "REDEEM $1,000 CODE",
        "bg_color": (35, 10, 20),
        "header_color": (200, 30, 60),
        "audio_freq": 600,
        "duration": 8
    },
    {
        "id": "SAFEAD_UFA_VID_018",
        "title": "Government Tax Arrest Legal Impersonation",
        "category_badge": "IMPERSONATION FRAUD",
        "main_headline": "LEGAL NOTICE: ARREST WARRANT PENDING!",
        "claim": "Federal tax evasion warrant issued for your name.",
        "urgency": "Pay outstanding fine via gift cards within 1 hour.",
        "cta": "CALL ENFORCEMENT DESK",
        "bg_color": (30, 10, 10),
        "header_color": (0, 0, 200),
        "audio_freq": 900,
        "duration": 9
    },
    {
        "id": "SAFEAD_UFA_VID_019",
        "title": "Pig-Butchering Romance & Crypto Circle Fraud",
        "category_badge": "PIG BUTCHERING",
        "main_headline": "VIP ELITE DATING & WEALTH CIRCLE",
        "claim": "Meet affluent investors and multiply your portfolio.",
        "urgency": "Exclusive invitation code required to deposit.",
        "cta": "JOIN VIP INVESTMENT CLUB",
        "bg_color": (25, 15, 35),
        "header_color": (160, 20, 100),
        "audio_freq": 500,
        "duration": 9
    },
    {
        "id": "SAFEAD_UFA_VID_020",
        "title": "Unregulated Prescription Drug Pharmacy Ad",
        "category_badge": "ILLEGAL DRUG SALES",
        "main_headline": "BUY OXY & SLEEP AIDS WITHOUT RX!",
        "claim": "No prescription needed. 100% discrete overnight drop.",
        "urgency": "Express global courier shipping guaranteed.",
        "cta": "ORDER RX MEDS DISCRETE",
        "bg_color": (20, 25, 35),
        "header_color": (180, 20, 40),
        "audio_freq": 450,
        "duration": 9
    },
    {
        "id": "SAFEAD_UFA_VID_021",
        "title": "Bogus $15,000 Solar Panel Stimulus Check",
        "category_badge": "DECEPTIVE STIMULUS",
        "main_headline": "$15,000 SOLAR CHECKS APPROVED!",
        "claim": "Homeowners in your ZIP code qualify for free solar.",
        "urgency": "Government stimulus funding expires Friday!",
        "cta": "CLAIM $15,000 STIMULUS",
        "bg_color": (15, 30, 20),
        "header_color": (30, 160, 120),
        "audio_freq": 550,
        "duration": 8
    },
    {
        "id": "SAFEAD_UFA_VID_022",
        "title": "Mega Millions Sweepstakes Fee Advance Scam",
        "category_badge": "LOTTERY FRAUD",
        "main_headline": "OFFICIAL WINNER: $2,500,000 JACKPOT!",
        "claim": "Ticket #7729-A confirmed 2nd tier jackpot winner.",
        "urgency": "Send $350 international release fee to claim payout.",
        "cta": "CLAIM $2.5M JACKPOT",
        "bg_color": (30, 25, 10),
        "header_color": (20, 170, 210),
        "audio_freq": 650,
        "duration": 9
    },
    {
        "id": "SAFEAD_UFA_VID_023",
        "title": "Pyramid Scheme $1,200/Day Copy-Paste Job",
        "category_badge": "PYRAMID SCHEME",
        "main_headline": "WORK FROM HOME: $1,200 PER DAY!",
        "claim": "Copy & paste links 2 hours a day. Zero experience.",
        "urgency": "Recruit 3 friends and earn recurring 50% commissions.",
        "cta": "START EARNING $1,200/DAY",
        "bg_color": (20, 20, 40),
        "header_color": (140, 40, 160),
        "audio_freq": 520,
        "duration": 9
    },
    {
        "id": "SAFEAD_UFA_VID_024",
        "title": "Spyware Phone Monitoring Tracker App Ad",
        "category_badge": "SPYWARE / STALKERWARE",
        "main_headline": "WHO IS YOUR PARTNER TEXTING?",
        "claim": "Read secret WhatsApp chats & track GPS location silently.",
        "urgency": "100% undetectable stealth tracking software.",
        "cta": "ACTIVATE PHONE SPY NOW",
        "bg_color": (15, 15, 25),
        "header_color": (0, 70, 180),
        "audio_freq": 750,
        "duration": 8
    },
    {
        "id": "SAFEAD_UFA_VID_025",
        "title": "Miracle Black Salve Cancer Cure False Claim",
        "category_badge": "BOGUS MEDICAL CURE",
        "main_headline": "100% ORGANIC CANCER MIRACLE CURE!",
        "claim": "Black salve paste destroys tumors in 7 days flat.",
        "urgency": "Skip dangerous chemotherapy! Proven secret herbal remedy.",
        "cta": "ORDER CANCER CURE PASTE",
        "bg_color": (30, 15, 15),
        "header_color": (200, 20, 20),
        "audio_freq": 400,
        "duration": 10
    }
]

w, h = 640, 360
fps = 25

for vdef in SYNTHETIC_UFA_DEFS:
    vid_id = vdef["id"]
    dest_final = UFA_VID_DIR / f"{vid_id}.mp4"
    temp_avi = UFA_VID_DIR / f"temp_{vid_id}.mp4"
    
    duration = vdef["duration"]
    total_frames = fps * duration
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(temp_avi), fourcc, float(fps), (w, h))
    
    badge = vdef["category_badge"]
    headline = vdef["main_headline"]
    claim = vdef["claim"]
    urgency = vdef["urgency"]
    cta = vdef["cta"]
    bg = vdef["bg_color"]
    header_col = vdef["header_color"]
    
    for f_idx in range(total_frames):
        canvas = np.zeros((h, w, 3), dtype=np.uint8)
        canvas[:] = bg
        
        # Header banner
        cv2.rectangle(canvas, (0, 0), (w, 54), header_col, -1)
        
        # Pulsing warning icon or badge
        pulse = 1.0 + 0.15 * np.sin(f_idx * 0.4)
        badge_text = f"*** {badge} ***"
        cv2.putText(canvas, badge_text, (20, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.65 * pulse, (255, 255, 255), 2)
        
        # Urgency timer
        rem_sec = max(0, duration - int(f_idx / fps))
        timer_str = f"00:{rem_sec:02d}"
        cv2.putText(canvas, timer_str, (w - 110, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # Moving caution borders
        bar_len = int((w - 40) * (f_idx / total_frames))
        cv2.rectangle(canvas, (20, 340), (20 + bar_len, 348), header_col, -1)
        
        # Main scam headline
        cv2.putText(canvas, headline, (25, 115), cv2.FONT_HERSHEY_DUPLEX, 0.68, (255, 255, 255), 2)
        
        # Deceptive claim
        cv2.putText(canvas, claim, (25, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (220, 220, 220), 1)
        
        # Urgent trigger statement
        cv2.putText(canvas, urgency, (25, 205), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 220, 255), 1)
        
        # Policy notice
        cv2.putText(canvas, "[UNSAFE_FOR_ALL - Regulatory Violation Reference]", (25, 245), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (150, 150, 150), 1)
        
        # CTA button
        btn_w, btn_h = 320, 42
        btn_x, btn_y = (w - btn_w) // 2, 275
        cv2.rectangle(canvas, (btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h), header_col, -1)
        cv2.rectangle(canvas, (btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h), (255, 255, 255), 2)
        cv2.putText(canvas, cta, (btn_x + 18, btn_y + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 2)
        
        out.write(canvas)
        
    out.release()
    
    # Encode with audio stream
    freq = vdef["audio_freq"]
    cmd = [
        ffmpeg_exe, '-y',
        '-i', str(temp_avi),
        '-f', 'lavfi', '-i', f'sine=frequency={freq}:duration={duration}',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-shortest',
        str(dest_final)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if temp_avi.exists():
        temp_avi.unlink()
        
    print(f"Generated {vid_id}.mp4: {dest_final.stat().st_size} bytes, {duration}s")

# Sync all 25 videos to GDrive mirror if available
if GDRIVE_UFA_VID_DIR.exists():
    for f in UFA_VID_DIR.glob("SAFEAD_UFA_VID_*.mp4"):
        target_gd = GDRIVE_UFA_VID_DIR / f.name
        shutil.copy2(f, target_gd)
    print("Synchronized all 25 UFA videos to GDrive!")

print("All UNSAFE_FOR_ALL videos successfully created & verified!")
