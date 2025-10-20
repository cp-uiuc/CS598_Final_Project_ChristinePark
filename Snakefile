import yaml, os
cfg = yaml.safe_load(open("config.yaml"))

# --- Coordinates (Taxi Zones) ---
ZONES_URL = cfg["zones_url"]
ZONES_ZIP_PATH = cfg["zones_zip_path"]
COORDINATES_PATH = cfg["coordinates_path"]

ZONES_LOOKUP = cfg["zones_lookup"]

# --- Ride Data (Monthly Parquet Downloads) ---
RIDE_DATA_PATH = cfg["ride_data_path"]   # e.g., data/in/rides
SUCCESS = os.path.join(RIDE_DATA_PATH, "_SUCCESS")

# --- Transformed Ride Data ---
TRANSFORMED_RIDE_DATA_PATH =  cfg["transformed_ride_data_path"]

WEATHER_PATH = cfg["weather_path"]

FINAL_CSV = cfg["final_csv"]


rule all:
    input:
        COORDINATES_PATH,
        SUCCESS, 
        TRANSFORMED_RIDE_DATA_PATH,
        ZONES_LOOKUP,
        WEATHER_PATH,
        FINAL_CSV

rule fetch_zones_zip:
    output: ZONES_ZIP_PATH
    params: url=ZONES_URL
    shell: r"""
        mkdir -p $(dirname {output})
        python - <<'PY'
import requests
r = requests.get("{params.url}"); r.raise_for_status()
open("{output}","wb").write(r.content)
PY
    """

# --- Transform ZIP → LocationID→borough lookup ---
rule make_zones_lookup:
    input: ZONES_ZIP_PATH
    output: ZONES_LOOKUP
    shell: r"""
        mkdir -p $(dirname {output})
        python scripts/make_zones_lookup.py {input} {output}
    """

rule transform_zones:
    input: ZONES_ZIP_PATH
    output: COORDINATES_PATH
    shell: r"""
        mkdir -p $(dirname {output})
        python scripts/compute_zone_coordinates.py {input} {output}
    """

rule fetch_ride_data:
    output: SUCCESS
    params:
        out_dir=RIDE_DATA_PATH,
    shell:
        r"""
        mkdir -p {params.out_dir}
        python scripts/fetch_ride_data.py {params.out_dir}
        """

rule transform_rides:
    input:
        success=SUCCESS,                 
        zones_lookup=ZONES_LOOKUP
    output:
        TRANSFORMED_RIDE_DATA_PATH
    params:
        rides_dir=RIDE_DATA_PATH
    shell:
        r"""
        python scripts/transform_rides_data.py {params.rides_dir} {input.zones_lookup} {output}
        """


rule fetch_weather_data:
    input:
        coords=COORDINATES_PATH
    output:
        WEATHER_PATH
    shell:
        r"""
        mkdir -p $(dirname {output})
        python scripts/fetch_weather_data.py {input.coords} {output}
        """

rule combine_rides_weather:
    input:
        agg=TRANSFORMED_RIDE_DATA_PATH,
        wx=WEATHER_PATH
    output:
        FINAL_CSV
    shell: 
        r"""
        python scripts/combine_rides_weather.py {input.agg} {input.wx} {output}
        """