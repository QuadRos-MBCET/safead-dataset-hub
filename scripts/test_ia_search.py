import urllib.request
import urllib.parse
import json

headers = {"User-Agent": "SafeAdCollector/1.0 (contact: juwel@safead.local)"}

def search_ia(q):
    url = f"https://archive.org/advancedsearch.php?q={urllib.parse.quote(q)}&fl[]=identifier,title,description&rows=5&output=json"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read().decode("utf-8"))
        docs = d.get("response", {}).get("docs", [])
        print(f"IA Query [{q}]: {len(docs)} results")
        for doc in docs:
            ident = doc.get("identifier")
            title = doc.get("title")
            print(f"   - {ident}: {title}")
    except Exception as e:
        print(f"IA Error for {q}: {e}")

if __name__ == "__main__":
    search_ia("collection:(classic_tv_commercials) beer")
    search_ia("collection:(classic_tv_commercials) cigarette")
    search_ia("collection:(classic_tv_commercials) casino")
    search_ia("collection:(classic_tv_commercials) gambling")
    search_ia("collection:(classic_tv_commercials) PSA")
