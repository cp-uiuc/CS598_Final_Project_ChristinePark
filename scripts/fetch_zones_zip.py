import sys, time, requests
from pathlib import Path

def fetch(url: str, out_path: str, retries: int = 5, backoff: float = 0.5):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    for i in range(retries + 1):
        try:
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            with open(out_path, "wb") as f:
                f.write(r.content)
            return
        except Exception:
            if i == retries:
                raise
            time.sleep(backoff * (2 ** i))

if __name__ == "__main__":
    url, outp = sys.argv[1], sys.argv[2]
    fetch(url, outp)
