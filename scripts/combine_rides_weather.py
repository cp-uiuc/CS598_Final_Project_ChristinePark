import sys, polars as pl

agg_parquet, weather_parquet, out_csv = sys.argv[1], sys.argv[2], sys.argv[3]

agg = pl.scan_parquet(agg_parquet).with_columns(
    pl.col("hour_start").cast(pl.Datetime)
)
wx = pl.scan_parquet(weather_parquet).with_columns(
    pl.col("hour_start").cast(pl.Datetime)
)

final = (
    agg
    .join(wx, on=["borough", "hour_start"], how="left")
    .select(
        "borough",
        "date",
        "hour_start",
        "rides",
        pl.all().exclude(["borough","date","hour_start","rides"])  # weather cols
    )
    .collect(engine="streaming")
)

final.write_csv(out_csv)
print(f"Wrote {out_csv}, rows={final.height}")
