FROM python:3.12-slim

# Required packages to compile geospatial Python libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gdal-bin \
        libgdal-dev \
        build-essential \
        && rm -rf /var/lib/apt/lists/*

#Install uv
RUN pip install uv==0.9.2

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

ENV POLARS_MAX_THREADS=2 \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    GDAL_NUM_THREADS=1

ENTRYPOINT ["snakemake"]
CMD ["-c", "1"]