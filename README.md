# NYC FHVHV–Weather Integration Pipeline

## Overview

This project builds a reproducible workflow to integrate 2023 NYC for-hire vehicle (FHVHV) trip data with Open-Meteo hourly weather data.
The pipeline uses Snakemake for workflow management and Polars for scalable data transformation.
Outputs include borough-hour–level ride aggregates joined with hourly weather variables.

## Workflow
Step | Script / Rule | Description
--- | --- | ---
1 | fetch_ride_data.py | Downloads monthly 2023 FHVHV Parquet files
2 | fetch_weather_data.py | Retrieves hourly weather for each borough
3 | compute_zone_coordinates.py | Extracts NYC borough coordinates
4 | transform_rides_data.py | Cleans and aggregates rides by borough and hour
5 | combine_rides_weather.py | Joins aggregated rides with hourly weather
6 | write_meta.py | Generates provenance and metadata sidecars

## Directory Layout
```
data/
├── in/               # Raw data (e.g., ride parquet files, taxi_zones.zip)
├── tmp/              # Intermediate results (zones lookup, weather, transformed data)
└── out/              # Final combined datasets

scripts/              # All processing scripts
```

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
* Requests
* Open-Meteo-Requests
* Requests-Cache


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
* Next: add metadata and provenance tracking to document data lineage and reproducibility