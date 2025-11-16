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
Project layout:
CS598_Final_Project_ChristinePark/
├── Snakefile
├── config.yaml
├── pyproject.toml
├── scripts/
│   ├── fetch_ride_data.py           # Download monthly 2023 FHVHV Parquet files
│   ├── compute_zone_coordinates.py  # Compute borough-level coordinates
│   ├── make_zones_lookup.py         # Map TLC LocationIDs to boroughs
│   ├── transform_rides_data.py      # Clean and aggregate rides by borough-hour
│   ├── fetch_weather_data.py        # Retrieve hourly weather from Open-Meteo
│   └── combine_rides_weather.py     # Join aggregated rides with hourly weather
├── data/
│   ├── in/      # Raw inputs (downloaded data). Not tracked in Git; available via Box link.
│   ├── tmp/     # Intermediate transformation outputs. Not tracked in Git; available via Box.
│   └── out/     # Final outputs. Includes citywide_hourly_2023.csv (tracked in Git).
├── metadata/
│   ├── dataset.jsonld        # schema.org Dataset metadata
│   └── data_dictionary.pdf   # Variable definitions and descriptions
├── provenance/
│   ├── dag.png    # Example expanded workflow DAG (for reference)
│   └── rules.png  # Example rule-level dependency graph (for reference)
└── README.md
```

## Metadata
The `metadata/` directory provides documentation for the final dataset:
* `dataset.jsonld` - schema.org JSON-LD describing dataset structure, variables, and workflow
* `data_dictionary.pdf` - documentation for each variable in the final CSV.

These files describe only the **final dataset** stored in `data/out/`.


## Important Note about `data/`
The `data/in/` and `data/tmp/` directories are not included in this repository because the raw and intermediate files are too large for GitHub. These directories are generated automatically when the Snakemake workflow runs.

For reference and validation, copies of the raw inputs and intermediate outputs are available in Box:
**[https://uofi.box.com/s/2oommk4mla932lrpy89h6rmts1k06zq3](https://uofi.box.com/s/2oommk4mla932lrpy89h6rmts1k06zq3)**

Only the final outputs in `data/out/` are tracked in this repository.


## Running the Pipline with Docker Compose
This project provides a prebuilt Docker image on Docker Hub to ensure reproducibility and provenance across all environments. The included `docker-compose.yaml` runs the workflow using this published image and mounts a host data directory into the container so that all inputs, intermediates, outputs, Snakemake internal state (e.g. Snakemake logs) persist on your machine.

Both the data directory and the Snakemake state directory can be customized at runtime using environment variables.


### Data Directory Selection (Dynamic)

The Compose configuration uses:
```yaml
volumes:
    - ${DATA_DIR:-./data}:/app/data
    - ${SNAKEMAKE_DIR:-./.snakemake}:/app/.snakemake
```

This means:
* If `DATA_DIR` is set -> that path is used
* If not set -> the default `./data` is used

#### Example: Use the default ./data directory
```bash
docker compose run pipeline
```

Outputs will appear under:
```bash
./data/
```

Snakemake's internal metadata and logs will appear under:
```bash
./snakemake/
```

#### Example: Use custom directories
**Relative path (recommended):**
```bash
DATA_DIR=./custom_data \
SNAKEMAKE_DIR=./.custom_snakemake \
docker compose run pipeline
```

**Absolute paths (supported if Docker has access):**
```bash
DATA_DIR=/valid/absolute/custom_data \
SNAKEMAKE_DIR=/valid/absolute/.custom_snakemake \
docker compose run pipeline
```

### Running a Specific Rule
To run a single Snakemake rule via Docker Compose, you need to pass the core count explicitly.

This is because the `docker-compose.yaml` provides a default command (e.g., `["-c", "1"]`), but when you add extra arguments on the CLI, you override that default and must include `-c` yourself.

**Example**:
```bash
docker compose run pipeline -c 1 transform_rides
```
Here:
* `pipeline` is the docker compose service name
* `-c 1` tells Snakemake to use 1 core
* `transform_rides` is the rule to execute


## Container Image Provenance
This workflow is executed using a published Docker image to ensure environment consistency and reproducibility.

Docker Image:
```
cp60uiuc/nyc-fhvhv-weather-integration-pipeline:v1
```

Image Digest:
```
sha256:f75d871c95acbe573f3e2b24d60c39bc4e08d446568c8457c076a30f1ddb042b
```

The digest uniquely identifies the exact image used to run the workflow.
The `docker-compose.yaml` configuration references this published image so all users run the pipeline in the same environment.

## Workflow Visualizations

Snakemake can generate workflow graphs by piping DOT output through Graphviz (`dot`).
These commands run Snakemake inside Docker but write the resulting images to your **host** filesystem.

**Make sure the directory you write the file into already exists.**

You may choose any output path (e.g., `provenance/`, `figures/`, `.`), but the directory must exist first.

**For convenience, this repository includes example images in the provenance/ folder as a reference.**

### Rule Graph
```bash
docker compose run pipeline --rulegraph | dot -Tpng > path/to/output/rules.png
```

![rules.png](provenance/rules.png)

### Workflow DAG
```bash
docker compose run pipeline --dag | dot -Tpng > path/to/output/dag.png
```
![dag.png](provenance/dag.png)


## (Optional) Local Development Environment

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


## (Optional) Running the Pipeline Locally

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