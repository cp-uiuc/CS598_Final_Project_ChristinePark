# NYC FHVHV–Weather Integration Pipeline

## Overview

This project builds a reproducible workflow to integrate 2023 NYC for-hire vehicle (FHVHV) trip data with Open-Meteo hourly weather data.
The pipeline uses Snakemake for workflow management and Polars for scalable data transformation.
Outputs include borough-hour–level ride aggregates joined with hourly weather variables.

## Workflow
Step | Snakemake Rule | Script | Description | Primary Data Artifact(s)
--- | --- | --- | --- | ---
1 | `fetch_zones_zip` | `fetch_zones_zip.py` | Downloads taxi zone zip file | `data/in/zones/taxi_zones.zip`
2 | `make_zones_lookup` | `make_zones_lookup.py` | Maps taxi zone `LocationIDs` to boroughs. | `data/tmp/zones_lookup.csv`
3 | `transform_zones` | `compute_zone_coordinates.py` | Extracts NYC borough coordinates | `data/tmp/borough_coordinates.csv`
4 | `fetch_ride_data` | `fetch_ride_data.py` | Downloads monthly 2023 FHVHV Parquet files | `data/in/rides/*.parquet`
5 | `transform_rides` | `transform_rides_data.py` | Cleans and aggregates rides by borough and hour | `data/tmp/rides_transformed.parquet`
6 | `fetch_weather_data` | `fetch_weather_data.py` | Retrieves hourly weather for each borough | `data/in/hourly_weather_2023.parquet`
7 | `combine_rides_weather` | `combine_rides_weather.py` | Joins aggregated rides with hourly weather | `data/out/citywide_hourly_2023.csv`

## Project Structure
```
CS598_Final_Project_ChristinePark/
├── Snakefile
├── config.yaml
├── pyproject.toml
├── scripts/
│   ├── fetch_ride_data.py
│   ├── compute_zone_coordinates.py
│   ├── make_zones_lookup.py
│   ├── transform_rides_data.py
│   ├── fetch_weather_data.py
│   └── combine_rides_weather.py
├── data/           # Not included in repo due to size limits
│   ├── in/         # Raw inputs (downloaded data)
│   ├── tmp/        # Intermediate transformations
│   └── out/        # Final outputs
└── README.md

```

⚠️ **Important Note:**
The `data/` directory is not included in this repository because the generated files are too large for GitHub. All input, intermediate, and final data outputs are stored in **[Box](https://uofi.box.com/s/2oommk4mla932lrpy89h6rmts1k06zq3)** for validation and comparison. When you run the pipeline locally, these files will be automatically generated in the `data/` directory.

## Environment Setup

The project uses [uv](https://docs.astral.sh/uv/) for Python environment management.

1. Install `uv` if not already installed:

```bash
pip install uv
```

2. Create a virtual environment using `uv` (defaults to .venv):
```bash
uv venv
```

3. Activate the environment:
```bash
source .venv/bin/activate
```

4. Install dependencies:
```bash
uv sync
```
This installs all dependencies from pyproject.toml into .venv.

### Key Packages
* Python ≥ 3.12
* Snakemake ≥ 8
* Polars
* Geopandas
* Open-Meteo-Requests


## Running the Pipeline

Run the complete workflow:

```bash
snakemake -c 4
```

Or execute a specific step, for example:

```bash
snakemake -c 2 transform_rides
```

## Configuration

All paths and URLs are defined in config.yaml


## Current Status

* Environment and Snakemake workflow established
* Ride and weather data ingestion complete
* Transformation and aggregation implemented

## Next Steps
* Add metadata files describing dataset sources, structure, and variables.
* Record data provenance to trace how each output was created.
* Verify data consistency and validate final results.
