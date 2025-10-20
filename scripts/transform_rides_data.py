import sys, os, glob, polars as pl
from pathlib import Path

REQ_COLS = {
    "request_datetime": pl.Datetime,
    "PULocationID": pl.Int64,
    "trip_miles": pl.Float64,
    "trip_time": pl.Int64,
}

def main(in_dir: str, zones_lookup: str, out_path: str):
    parts = sorted(glob.glob(os.path.join(in_dir, "fhvhv_tripdata_*.parquet")))
    assert parts, f"No inputs in {in_dir}"

    # lazy read, column prune
    rides = pl.scan_parquet(parts, cast_options=pl.ScanCastOptions(integer_cast="upcast")).select(list(REQ_COLS.keys()))

    # validations
    rides = (
        rides
        .with_columns([
            pl.col("request_datetime").cast(pl.Datetime, strict=False),
            pl.col("PULocationID").cast(pl.Int64, strict=False),
            pl.col("trip_miles").cast(pl.Float64, strict=False),
            pl.col("trip_time").cast(pl.Int64, strict=False),
        ])
        .filter(pl.all_horizontal(
            pl.col("request_datetime").is_not_null(),
            (pl.col("trip_miles") >= 0),
            (pl.col("trip_time") >= 0),
            pl.col("PULocationID").is_not_null(),
        ))
    )

    # load zones lookup
    zones = pl.read_csv(zones_lookup).with_columns(
        pl.col("LocationID").cast(pl.Int64)
    )

    agg_rides_with_boroughs = (
        rides
        .join(zones.lazy(), left_on="PULocationID", right_on="LocationID", how="inner")
        .with_columns([
            (pl.col("request_datetime").dt.truncate("1h")).alias("hour_start"),
            (pl.col("request_datetime").dt.date().alias("date")),
        ])
        .group_by(["borough", "date", "hour_start"])
        .agg(pl.len().alias("rides"))
        .sort(["borough", "date", "hour_start"])
    )

    count = agg_rides_with_boroughs.collect().height
    print(count)

    Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)
    agg_rides_with_boroughs.collect(engine="streaming").write_parquet(out_path)

if __name__ == "__main__":
    in_dir, zones_lookup, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    main(in_dir, zones_lookup, out_path)
