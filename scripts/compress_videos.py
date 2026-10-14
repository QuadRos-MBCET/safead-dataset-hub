import os
import subprocess
import shutil
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
print(f"FFmpeg binary: {ffmpeg_exe}")

pairs = [
    (
        r"C:\Users\Asus\Desktop\Dataset\custom_ads\safe_18_plus\videos\SAFEAD_S18P_VID_007.mp4",
        r"C:\Users\Asus\Desktop\safead\safead-dataset-hub\custom_ads\safe_18_plus\videos\SAFEAD_S18P_VID_007.mp4"
    ),
    (
        r"C:\Users\Asus\Desktop\Dataset\custom_ads\unsafe_for_all\videos\SAFEAD_UFA_VID_004.mp4",
        r"C:\Users\Asus\Desktop\safead\safead-dataset-hub\custom_ads\unsafe_for_all\videos\SAFEAD_UFA_VID_004.mp4"
    )
]

for desk_p, repo_p in pairs:
    target_p = desk_p if os.path.exists(desk_p) else repo_p
    if not os.path.exists(target_p):
        print(f"File not found: {target_p}")
        continue
    
    orig_mb = os.path.getsize(target_p) / (1024 * 1024)
    print(f"Processing {os.path.basename(target_p)}: original size = {orig_mb:.2f} MB")
    
    tmp_out = target_p + ".compressed.mp4"
    # Re-encode to CRF 28, fast preset, max 720p height, audio 128k AAC
    cmd = [
        ffmpeg_exe, "-y",
        "-i", target_p,
        "-vf", "scale=-2:'min(720,ih)'",
        "-c:v", "libx264",
        "-crf", "28",
        "-preset", "veryfast",
        "-c:a", "aac",
        "-b:a", "128k",
        tmp_out
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res.returncode == 0 and os.path.exists(tmp_out):
        new_mb = os.path.getsize(tmp_out) / (1024 * 1024)
        print(f"Successfully compressed to {new_mb:.2f} MB")
        shutil.move(tmp_out, desk_p)
        shutil.copy2(desk_p, repo_p)
        print(f"Updated both Dataset and repo copies of {os.path.basename(target_p)}")
    else:
        print(f"Compression failed with code {res.returncode}")

print("All done!")
