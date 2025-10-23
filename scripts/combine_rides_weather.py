import sys, polars as pl

agg_parquet, weather_parquet, out_csv = sys.argv[1], sys.argv[2], sys.argv[3]

agg = pl.scan_parquet(agg_parquet).with_columns(
    pl.col("timestamp_hour").cast(pl.Datetime)
)
wx = pl.scan_parquet(weather_parquet).with_columns(
    pl.col("timestamp_hour").cast(pl.Datetime)
)

final = (
    agg
    .join(wx, on=["borough", "timestamp_hour"], how="left")
    .select(
        "borough",
        "date",
        "timestamp_hour",
        "ride_count",
        pl.all().exclude(["borough","date","timestamp_hour","ride_count"])  # weather cols
    )
    .collect(engine="streaming")
)

final.write_csv(out_csv)
print(f"Wrote {out_csv}, rows={final.height}")
