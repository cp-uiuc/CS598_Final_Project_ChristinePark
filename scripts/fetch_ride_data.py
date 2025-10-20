import sys, time
from pathlib import Path
import requests

URLS = [
    "https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_2023-01.parquet",
    "https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_2023-02.parquet",
    "https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_2023-03.parquet",
    "https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_2023-04.parquet",
    "https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_2023-05.parquet",
    "https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_2023-06.parquet",
    "https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_2023-07.parquet",
    "https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_2023-08.parquet",
    "https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_2023-09.parquet",
    "https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_2023-10.parquet",
    "https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_2023-11.parquet",
    "https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_2023-12.parquet",
]

def download(url: str, dest: Path, timeout=300, max_retries=6, base_backoff=5):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    tries = 0
    while True:
        try:
            with requests.get(url, stream=True, timeout=timeout) as r:
                r.raise_for_status()
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1 << 20):
                        if chunk:
                            f.write(chunk)
            tmp.replace(dest)
            return
        except Exception as e:
            tries += 1
            if tries > max_retries:
                raise
            sleep_s = min(base_backoff * (2 ** (tries - 1)), 300)
            print(f"retry {tries}/{max_retries} after {sleep_s}s: {e}")
            time.sleep(sleep_s)

def main(out_dir: str):
    outp = Path(out_dir)
    for url in URLS:
        name = url.rsplit("/", 1)[-1]
        dest = outp / name
        if dest.exists():
            print(f"skip {dest}")
        else:
            print(f"downloading {url} -> {dest}")
            download(url, dest)
        
        time.sleep(2)

    print(f"done: files in {out_dir}")
    Path(out_dir, "_SUCCESS").write_text("ok\n")
    print(f"Done: all 2023 ride data files downloaded to {out_dir}")

if __name__ == "__main__":
    out_dir = sys.argv[1]
    main(out_dir)
