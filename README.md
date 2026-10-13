# SafeAd AI — Sourav's Contribution Branch (`sourav`)

Collaborative dataset branch maintained by **Sourav** for the **SafeAd AI / SAFE-VISION** multimodal advertisement content safety and audience classification project.

- **Assigned Categories**: `SAFE_FOR_ALL` and `SAFE_14_PLUS`
- **Branch**: `sourav`
- **Manifest**: [`manifests/sourav/contribution_manifest.json`](manifests/sourav/contribution_manifest.json)
- **Google Drive Storage**: `G:\My Drive\SafeAd_Dataset\custom_ads\`

---

## 📦 What This Branch Contains

### 1. Curated Genuine Dataset (162 Validated Samples)

| Modality | `SAFE_FOR_ALL` | `SAFE_14_PLUS` | Total | Verification & Features |
|---|---:|---:|---:|---|
| **Real Photos (Images)** | 75 | 75 | **150** | Verified with Pillow (`PIL.Image.open`), high resolution (HD to 4K), 0 duplicates, true SHA-256 hashes. |
| **Real Videos (with Audio & Text)** | 7 | 5 | **12** | Standardized H.264 + AAC Stereo MP4s, audible dialogue/music, on-screen text/titles, 5s–5min runtime, ~3MB average size. |
| **Total Samples** | **82** | **80** | **162** | **100% compliant with schema and policy.** |

---

### 2. Diverse Real-World Topics (Images)

- **`SAFE_FOR_ALL` (75 Photos)**:
  - *Appliances & Kitchen*: Electric toaster, smoothie blender, stainless electric kettle, family refrigerator, drip coffee maker, teapot, cutting board, liquid measuring cup, soup spoons.
  - *Groceries & Food*: Sliced whole wheat bread, eggs carton, pure honey jar, olive oil bottle, pasta box, rolled oats, white rice bag, vegetable soup, fresh orange juice, fruit bowl.
  - *Home & Domestic Life*: Living room sofa couch, dining chair, wooden bookshelf, sleeping pillow, coffee mugs, ceramic plates, indoor potted houseplants, clean folded towels, laundry hamper.
  - *School & Child Development*: Wax crayons box, desk pencil sharpener, wooden metric rulers, jigsaw puzzles, origami cranes, classroom globe, plush teddy bear, magnifying glass.
  - *Utilities & Public Life*: Garden watering can, brass padlock, folding umbrella, LED flashlight, measuring tape, reusable shopping tote, public park bench, crosswalk, recycling bin, yellow school bus, passenger train.

- **`SAFE_14_PLUS` (75 Photos)**:
  - *Youth Apparel & Footwear*: High-top athletic sneakers, graphic streetwear hoodie, blue denim jacket, snapback caps, ribbed beanies, combat boots, casual leather belts, cargo utility pants, bomber jackets.
  - *Gaming & Esports Gear*: Wireless gaming controllers, RGB mechanical keyboards, high-DPI gaming mice, esports headsets, console game discs, HD webcams, racing steering wheels, handheld consoles, arcade fight sticks.
  - *Teen Sports & Athletics*: Skateboard decks with grip tape, BMX trick bikes, gym dumbbells, sparring boxing gloves, inline skates, basketballs, soccer balls, tennis rackets, pull-up bars, rock climbing harnesses, ping-pong paddles, badminton sets, surfboards, bouldering shoes.
  - *Youth Grooming & Skincare*: Blemish cleanser tubes, exfoliating facial scrubs, electric hair clippers, soothing aftershave balms, body spray canisters, lip balm sticks, matte styling clay wax.
  - *Teen Snacks & Beverages*: Instant spicy ramen noodles, habanero hot pepper sauces, cold brew coffee cans, chocolate protein bars, electrolyte sports drinks, beef jerky snacks, Doritos tortilla chips.
  - *Music & Youth Hobbies*: Electric guitars & amps, snare drums, electronic synthesizers, vinyl turntable players, action manga books, DSLR zoom cameras, quadcopter camera drones, skatepark transition bowls.

---

### 3. Authentic Video Collection (Video + Audio + Text)

All videos are authentic broadcasts and open cinema films with synchronized audio and visible on-screen text:

#### `SAFE_FOR_ALL` Videos (`custom_ads/safe_ad_for_all/videos/`):
1. **`SAFEAD_SFA_VID_001.mp4`**: Kellogg's Frosted Flakes TV Commercial (1976) — Tony the Tiger voiceover + jingle + *"They're Gr-r-reat!"* slogan text (30.2s, 2.9 MB).
2. **`SAFEAD_SFA_VID_002.mp4`**: Vintage Coca-Cola Commercial (1954) — Announcer speech + music + *"Drink Coca-Cola"* logo typography (56.6s, 3.1 MB).
3. **`SAFEAD_SFA_VID_003.mp4`**: Post Sugar Crisp Cereal Commercial — Sugar Bear singing jingle + character dialogue + printed box text (100.0s, 3.2 MB).
4. **`SAFEAD_SFA_VID_004.mp4`**: DuMont Television Set Commercial — Narrator speech + on-screen brand name and technical display text (90.6s, 3.0 MB).
5. **`SAFEAD_SFA_VID_005.mp4`**: Kellogg's Sugar Smacks Commercial — Animated voice acting + cereal box graphics (138.0s, 6.6 MB).
6. **`SAFEAD_SFA_VID_006.mp4`**: UNIVAC Computer Commercial (1956) — Narration + printed computer console typography (28.0s, 1.3 MB).
7. **`SAFEAD_SFA_VID_007.mp4`**: Big Buck Bunny Animated Film Trailer — Orchestral score + main title card and production credits (33.0s, 1.7 MB).

#### `SAFE_14_PLUS` Videos (`custom_ads/safe_14_plus/videos/`):
1. **`SAFEAD_S14P_VID_001.mp4`**: DeSoto Sports Automobile Commercial — Engine sounds + driving narration + chrome vehicle badging and slogan text (82.0s, 3.2 MB).
2. **`SAFEAD_S14P_VID_002.mp4`**: Shasta Soda Monster Halloween Commercial — Frankenstein monster voiceover + eerie sound effects + Shasta logo text (56.4s, 2.8 MB).
3. **`SAFEAD_S14P_VID_003.mp4`**: Trik Trak High-Speed Stunt Track Commercial — Announcer voiceover + racing sound FX + action typography (60.1s, 2.7 MB).
4. **`SAFEAD_S14P_VID_004.mp4`**: 1960 Televised Campaign Commercial with Jingle — Campaign jingle + candidate speech + banners and placards (59.8s, 2.2 MB).
5. **`SAFEAD_S14P_VID_005.mp4`**: 1955 Teen Diner / Drive-In Commercial — Teen dialogue + pop music + glowing neon sign text (110.0s, 5.9 MB).

---

### 4. Cloud Storage Layout (Google Drive)

All media binaries are synchronized with Google Drive Desktop:
```
G:\My Drive\SafeAd_Dataset\custom_ads\
├── safe_ad_for_all\
│   ├── images\                         (75 genuine photos: SAFEAD_SFA_IMG_001.jpg - 075.jpg)
│   └── videos\                         (7 real videos with sound & text: SAFEAD_SFA_VID_001.mp4 - 007.mp4)
├── safe_14_plus\
│   ├── images\                         (75 genuine photos: SAFEAD_S14P_IMG_001.jpg - 075.jpg)
│   └── videos\                         (5 real videos with sound & text: SAFEAD_S14P_VID_001.mp4 - 005.mp4)
└── complete_dataset_catalog.csv         (Full metadata spreadsheet catalog)
```

---

### 5. Automated Tooling & Scripts

- **`scripts/download_audiotext_videos.py`**: Downloads and verifies authentic open videos with audio streams and on-screen text.
- **`scripts/scale_to_75_images.py`**: Automated pipeline for genuine image collection across wide topic pools.
- **`scripts/export_for_training.py`**: Converts manifest data into PyTorch / TensorFlow ready CSV or JSONL training splits.
- **`scripts/sync_storage.py`**: Cloud storage footprint inspector and Google Drive / rclone sync utility.
- **`tools/validate_manifest.py`**: Validates schema compliance, path portability, label policy, and SHA-256 uniqueness.

---

## 🚀 How to Run & Verify

1. **Validate Manifest**:
   ```powershell
   python tools/validate_manifest.py manifests/sourav/contribution_manifest.json
   ```

2. **Run Unit Tests**:
   ```powershell
   python -m unittest discover tests
   ```

3. **Export Training Data (CSV)**:
   ```powershell
   python scripts/export_for_training.py csv
   ```
