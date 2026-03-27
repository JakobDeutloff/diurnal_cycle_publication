# Diurnal Cycle Publication Repository

Code to reproduce figures and key numbers from Deutloff et al. (2026).

## Data
Download the required input data from Zenodo:

- https://doi.org/10.5281/zenodo.8344417

After downloading, edit the `get_path()` function in `src/read_data.py` to point to your local data directory.

## Python Environment
Create an environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Reproduce Figures
Run scripts from the repository root:

```bash
mkdir -p plots
```

```bash
python scripts/1d_diurnal_cycle.py
python scripts/2d_diurnal_cycle.py
python scripts/albedo.py
python scripts/autocorrelation.py
python scripts/bt_iwp.py
python scripts/cloud_field.py
python scripts/dc_radiation.py
python scripts/test_boostrapping.py
```

Outputs are written to `plots/`.
