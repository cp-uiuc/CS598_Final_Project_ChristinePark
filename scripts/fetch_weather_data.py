import sys, polars as pl
import openmeteo_requests, requests_cache
from retry_requests import retry

API = "https://archive-api.open-meteo.com/v1/archive"
TZ  = "America/New_York"
START = "2023-01-01"
END   = "2023-12-31"
HOURLY = ["temperature_2m","precipitation","wind_speed_10m","relative_humidity_2m"]

def fetch_hourly_pl(lat: float, lon: float) -> pl.DataFrame:
    cache = requests_cache.CachedSession(".cache", expire_after=-1)
    session = retry(cache, retries=5, backoff_factor=0.3)
    om = openmeteo_requests.Client(session=session)

    resp = om.weather_api(API, params={
        "latitude": lat, "longitude": lon,
        "start_date": START, "end_date": END,
        "timezone": TZ, "hourly": HOURLY
    })[0]

    h = resp.Hourly()
    t0 = h.Time()          # epoch seconds (UTC)
    t1 = h.TimeEnd()       # epoch seconds (UTC)
    step = h.Interval()    # seconds

    # build hourly timestamps in Polars (UTC -> NY)
    n = (t1 - t0) // step
    secs = pl.int_range(t0, t0 + n * step, step, eager=True)
    times = (
        pl.from_epoch(secs)
        .dt.replace_time_zone("UTC")
        .dt.convert_time_zone(TZ)
        .alias("hour_start")
    )

    cols = {"hour_start": times}
    for i, name in enumerate(HOURLY):
        cols[name] = pl.Series(name, h.Variables(i).ValuesAsNumpy())

    return pl.DataFrame(cols)

def main(centroids_csv: str, out_parquet: str):
    cents = pl.read_csv(centroids_csv)   # columns: borough, lon, lat
    frames = []
    for borough, lon, lat in cents.iter_rows():
        df = fetch_hourly_pl(lat=float(lat), lon=float(lon))
        frames.append(df.with_columns(pl.lit(borough).alias("borough")))
    weather = pl.concat(frames).select("borough","hour_start", *HOURLY).sort(["borough","hour_start"])
    pl.Config.set_tbl_rows(10)  # quick preview on run
    print(weather.head(10))
    weather.write_parquet(out_parquet)
    print(f"Wrote {out_parquet}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
