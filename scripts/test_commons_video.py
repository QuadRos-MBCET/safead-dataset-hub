import urllib.request
import urllib.parse
import json

headers = {"User-Agent": "SafeAdCollector/1.0 (contact: juwel@safead.local)"}

def search_commons_video(q):
    enc = urllib.parse.quote(f"{q} filetype:video")
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={enc}&gsrnamespace=6&gsrlimit=5&prop=imageinfo&iiprop=url|size|mime&format=json"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read().decode("utf-8"))
        pages = d.get("query", {}).get("pages", {})
        print(f"Commons Video [{q}]: {len(pages)} results")
        for pid, p in list(pages.items())[:3]:
            t = p.get("title")
            ii = p.get("imageinfo", [{}])[0]
            print(f"   - {t} ({ii.get('mime')}, {ii.get('size')} bytes)")
    except Exception as e:
        print(f"Commons Error for {q}: {e}")

if __name__ == "__main__":
    search_commons_video("beer commercial")
    search_commons_video("wine commercial")
    search_commons_video("alcohol advertisement")
    search_commons_video("gambling advertisement")
    search_commons_video("phishing")
    search_commons_video("scam warning")
    search_commons_video("fraud")
