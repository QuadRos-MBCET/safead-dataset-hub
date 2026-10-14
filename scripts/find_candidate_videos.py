import urllib.request
import urllib.parse
import json

headers = {"User-Agent": "SafeAdCollector/1.0 (contact: juwel@safead.local)"}

def find_mp4_items(query, max_items=5):
    q_enc = urllib.parse.quote(query)
    url = f"https://archive.org/advancedsearch.php?q={q_enc}&fl[]=identifier,title,description,mediatype&rows={max_items}&output=json"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode("utf-8"))
        docs = data.get("response", {}).get("docs", [])
        print(f"\n=== Results for: '{query}' ({len(docs)} found) ===")
        for d in docs:
            ident = d.get("identifier")
            title = d.get("title")
            meta_url = f"https://archive.org/metadata/{ident}"
            try:
                m_req = urllib.request.Request(meta_url, headers=headers)
                with urllib.request.urlopen(m_req, timeout=12) as mr:
                    m_data = json.loads(mr.read().decode("utf-8"))
                files = m_data.get("files", [])
                mp4_files = [
                    f for f in files 
                    if f.get("name", "").lower().endswith(".mp4") 
                    and not f.get("name", "").startswith(".")
                    and int(f.get("size", 0)) < 35 * 1024 * 1024  # under 35 MB
                ]
                if mp4_files:
                    # Choose a 512kb or standard mp4
                    chosen = mp4_files[0]
                    for f in mp4_files:
                        if "512kb" in f.get("name", "").lower() or "ia.mp4" in f.get("name", "").lower():
                            chosen = f
                            break
                    f_name = chosen.get("name")
                    f_size_mb = int(chosen.get("size", 0)) / (1024 * 1024)
                    f_url = f"https://archive.org/download/{ident}/{urllib.parse.quote(f_name)}"
                    print(f" - [{ident}] \"{title}\"")
                    print(f"   Size: {f_size_mb:.2f} MB")
                    print(f"   Direct URL: {f_url}")
            except Exception as me:
                pass
    except Exception as e:
        print(f"Search error for {query}: {e}")

if __name__ == "__main__":
    print("--- Searching for SAFE_18_PLUS candidates ---")
    find_mp4_items("collection:(classic_tv_commercials) AND (beer OR ale)", 4)
    find_mp4_items("collection:(classic_tv_commercials) AND (wine OR liquor)", 4)
    find_mp4_items("collection:(classic_tv_commercials) AND (cigarette OR tobacco)", 4)
    find_mp4_items("collection:(classic_tv_commercials) AND (casino OR gambling)", 4)

    print("\n--- Searching for UNSAFE_FOR_ALL candidates ---")
    find_mp4_items("collection:(classic_tv_commercials) AND (scam OR fraud OR fake)", 4)
    find_mp4_items("collection:(classic_tv_commercials) AND (drugs OR narcotics)", 4)
    find_mp4_items("collection:(prelinger) AND (quack OR patent medicine)", 4)
    find_mp4_items("collection:(prelinger) AND (fraud OR swindle)", 4)
