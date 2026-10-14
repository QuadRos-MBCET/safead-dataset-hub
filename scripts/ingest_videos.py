import os
import sys
import shutil
import subprocess
import urllib.request
import hashlib
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
print(f"Using FFmpeg: {ffmpeg_exe}")

repo_dir = r"C:\Users\Asus\Desktop\safead\safead-dataset-hub"
desktop_dir = r"C:\Users\Asus\Desktop\Dataset"

s18p_desktop_vids = os.path.join(desktop_dir, "custom_ads", "safe_18_plus", "videos")
s18p_repo_vids = os.path.join(repo_dir, "custom_ads", "safe_18_plus", "videos")
os.makedirs(s18p_desktop_vids, exist_ok=True)
os.makedirs(s18p_repo_vids, exist_ok=True)

ufa_desktop_vids = os.path.join(desktop_dir, "custom_ads", "unsafe_for_all", "videos")
ufa_repo_vids = os.path.join(repo_dir, "custom_ads", "unsafe_for_all", "videos")
os.makedirs(ufa_desktop_vids, exist_ok=True)
os.makedirs(ufa_repo_vids, exist_ok=True)

# 0. Clean up sample jpgs from ufa videos folder
for f in os.listdir(ufa_desktop_vids):
    if f.startswith("sample_") and f.endswith(".jpg"):
        try:
            os.remove(os.path.join(ufa_desktop_vids, f))
            print(f"Removed temp sample: {f}")
        except Exception as e:
            print(f"Failed to remove {f}: {e}")

# 1. Rename and ingest safe 18+ ads 008 through 022
ordered_new_s18p = [
    ("Commercial_Chesterfield_101_Cigarettes_A_silly_millimeter_longer_512kb.mp4", "SAFEAD_S18P_VID_008.mp4"),
    ("Commercial_Chesterfield_CigarettesDave_Madden_of_Partridge_Family_512kb.mp4", "SAFEAD_S18P_VID_009.mp4"),
    ("Commercial_Chesterfield_Cigarettes_21_great_tobaccos_jingle_512kb.mp4", "SAFEAD_S18P_VID_010.mp4"),
    ("Commercial_Chesterfield_Cigarettes_Favorite_of_sailors_1957_512kb.mp4", "SAFEAD_S18P_VID_011.mp4"),
    ("Commercial_Chesterfield_Cigarettes_Satisfies_the_most_512kb.mp4", "SAFEAD_S18P_VID_012.mp4"),
    ("Commercial_Chesterfield_Cigarettes_Tobaccoland_reporter_1951_512kb.mp4", "SAFEAD_S18P_VID_013.mp4"),
    ("Commercial_Chesterfield_Cigarettes_w_Jack_Webb_Dragnet_1950s_B-W_512kb.mp4", "SAFEAD_S18P_VID_014.mp4"),
    ("Commercial_Chesterfield_Cigarettes_w_the_Chesterfield_King_1962_512kb.mp4", "SAFEAD_S18P_VID_015.mp4"),
    ("Commercial_Old_Gold_Cigarettes_Dancing_Cigarette_Pack_512kb.mp4", "SAFEAD_S18P_VID_016.mp4"),
    ("Commercial_Old_Gold_Cigarettes_Old_Gold_filters_man_jingle_III_1970_512kb.mp4", "SAFEAD_S18P_VID_017.mp4"),
    ("Commercial_Old_Gold_Cigarettes_Old_Gold_filters_man_jingle_II_1970_512kb.mp4", "SAFEAD_S18P_VID_018.mp4"),
    ("Commercial_Old_Gold_Cigarettes_w_gift_star_coupons_1970_512kb.mp4", "SAFEAD_S18P_VID_019.mp4"),
    ("Commercial_Old_Gold_Cigarettes_w_Red_Barber_1948_512kb.mp4", "SAFEAD_S18P_VID_020.mp4"),
    ("Commercial_Old_Gold_King_Size_Cigarettes_Dancing_cigarette_packs_512kb.mp4", "SAFEAD_S18P_VID_021.mp4"),
    ("John Smith's Draught Beer Advert Variant 2.ia.mp4", "SAFEAD_S18P_VID_022.mp4")
]

for src_name, dst_name in ordered_new_s18p:
    src_p = os.path.join(s18p_desktop_vids, src_name)
    dst_desk_p = os.path.join(s18p_desktop_vids, dst_name)
    dst_repo_p = os.path.join(s18p_repo_vids, dst_name)
    if os.path.exists(src_p):
        shutil.move(src_p, dst_desk_p)
    if os.path.exists(dst_desk_p):
        shutil.copy2(dst_desk_p, dst_repo_p)
        print(f"Ingested {dst_name}: {os.path.getsize(dst_desk_p)/(1024*1024):.2f} MB")

# 2. Ingest casino_ad.mp4 as SAFEAD_S18P_VID_023.mp4
casino_src = r"C:\Users\Asus\Desktop\safead\main_project_s7\casino_ad.mp4"
if os.path.exists(casino_src):
    c_desk = os.path.join(s18p_desktop_vids, "SAFEAD_S18P_VID_023.mp4")
    c_repo = os.path.join(s18p_repo_vids, "SAFEAD_S18P_VID_023.mp4")
    shutil.copy2(casino_src, c_desk)
    shutil.copy2(casino_src, c_repo)
    print("Ingested SAFEAD_S18P_VID_023.mp4 from casino_ad.mp4")

# 3. Lucky Strike ads for 024 and 025
lucky_ads = [
    ("Commercial_Lucky_Strike_Cigarettes_1965_512kb.mp4", "SAFEAD_S18P_VID_024.mp4"),
    ("Commercial_Lucky_Strike_Cigarettes_Marching_Cigarettes_512kb.mp4", "SAFEAD_S18P_VID_025.mp4")
]
for arch_name, target_name in lucky_ads:
    target_desk = os.path.join(s18p_desktop_vids, target_name)
    target_repo = os.path.join(s18p_repo_vids, target_name)
    if not os.path.exists(target_desk) or os.path.getsize(target_desk) == 0:
        url = f"https://archive.org/download/Cigarette_Commercials_Lucky_Strike/{arch_name}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        print(f"Downloading {arch_name} -> {target_name}")
        with urllib.request.urlopen(req) as resp, open(target_desk, "wb") as out_f:
            shutil.copyfileobj(resp, out_f)
    shutil.copy2(target_desk, target_repo)
    print(f"Ingested {target_name}: {os.path.getsize(target_desk)/(1024*1024):.2f} MB")

# Sync existing 001-007
for i in range(1, 8):
    fname = f"SAFEAD_S18P_VID_{i:03d}.mp4"
    d_p = os.path.join(s18p_desktop_vids, fname)
    r_p = os.path.join(s18p_repo_vids, fname)
    if os.path.exists(d_p) and not os.path.exists(r_p):
        shutil.copy2(d_p, r_p)

# 4. Standardize unsafe videos
ordered_ufa = [
    ("1791991720tfDVw8Ls_oNrgg.mp4", "SAFEAD_UFA_VID_001.mp4"),
    ("16728109632083373.mp4", "SAFEAD_UFA_VID_002.mp4"),
    ("1676094514225119.mp4", "SAFEAD_UFA_VID_003.mp4"),
    ("1791994137fKcLBdYjtcdzPg+hd.mp4", "SAFEAD_UFA_VID_004.mp4")
]
for src_name, dst_name in ordered_ufa:
    src_p = os.path.join(ufa_desktop_vids, src_name)
    dst_desk_p = os.path.join(ufa_desktop_vids, dst_name)
    dst_repo_p = os.path.join(ufa_repo_vids, dst_name)
    if os.path.exists(src_p):
        shutil.move(src_p, dst_desk_p)
    if os.path.exists(dst_desk_p):
        shutil.copy2(dst_desk_p, dst_repo_p)
        print(f"Ingested {dst_name}: {os.path.getsize(dst_desk_p)/(1024*1024):.2f} MB")

# Ingest prototype unsafe videos
p_scam = r"C:\Users\Asus\Desktop\safead\main_project_s7\scam_giveaway.mp4"
if os.path.exists(p_scam):
    d_scam = os.path.join(ufa_desktop_vids, "SAFEAD_UFA_VID_005.mp4")
    r_scam = os.path.join(ufa_repo_vids, "SAFEAD_UFA_VID_005.mp4")
    shutil.copy2(p_scam, d_scam)
    shutil.copy2(p_scam, r_scam)
    print("Ingested SAFEAD_UFA_VID_005.mp4")

p_viol = r"C:\Users\Asus\Desktop\safead\main_project_s7\violence_ad.mp4"
if os.path.exists(p_viol):
    d_viol = os.path.join(ufa_desktop_vids, "SAFEAD_UFA_VID_006.mp4")
    r_viol = os.path.join(ufa_repo_vids, "SAFEAD_UFA_VID_006.mp4")
    shutil.copy2(p_viol, d_viol)
    shutil.copy2(p_viol, r_viol)
    print("Ingested SAFEAD_UFA_VID_006.mp4")

print("Finished Standardizing Media!")
