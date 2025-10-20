import sys, geopandas as gpd
zip_path, out_csv = sys.argv[1], sys.argv[2]

zones = gpd.read_file(f"zip://{zip_path}")
boroughs = zones.dissolve(by="borough")  # one geom per borough
centroids = boroughs.geometry.centroid.to_crs(4326) if boroughs.crs != 4326 else boroughs.geometry.centroid
out = (centroids.to_frame("geometry")
       .reset_index()
       .assign(lon=lambda d: d.geometry.x, lat=lambda d: d.geometry.y)
       [["borough","lon","lat"]])
out.to_csv(out_csv, index=False)
