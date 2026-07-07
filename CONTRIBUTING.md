# Contributing to SimNADES

Thanks for considering a contribution. SimNADES supports transparent, reproducible
simulation of natural deep eutectic solvent (NADES) systems for polyphenol
extraction.

## Development setup

Use Python 3.11 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On macOS or Linux, activate with:

```bash
source .venv/bin/activate
```

## Run the application

```powershell
streamlit run app.py
```

## Run checks

Before opening a pull request, run:

```powershell
python -m pytest -q
python -m ruff check app.py model.py data.py tests
python -m black --check app.py model.py data.py tests
```

If formatting is needed:

```powershell
python -m black app.py model.py data.py tests
```

## Pull requests

Please keep changes focused and describe:

- the scientific or software problem addressed;
- the files and model pathways changed;
- the tests or manual checks performed;
- any limitations, assumptions, or references relevant to the change.

Use conventional commits in Spanish when possible, for example:

```text
fix: corrige calculo de estabilidad termica
docs: actualiza referencias del paper JOSS
test: agrega cobertura para simulacion de tres pasos
```

## Scientific changes

Model updates should cite verifiable literature and avoid unreferenced constants
unless they are clearly marked as heuristic assumptions. Do not add DOIs or
bibliographic metadata unless they have been verified.
