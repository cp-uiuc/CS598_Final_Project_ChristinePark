import sys, geopandas as gpd

if __name__ == "__main__":
    zip_path, out_csv = sys.argv[1], sys.argv[2]
    gdf = gpd.read_file(f"zip://{zip_path}")

    valid = {"Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island", "EWR"}
    gdf = gdf[gdf["borough"].isin(valid)]

    gdf[["LocationID", "borough"]].drop_duplicates().to_csv(out_csv, index=False)
    print(f"Wrote {len(gdf)} records to {out_csv}")
