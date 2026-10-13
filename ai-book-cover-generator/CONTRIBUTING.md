# Contributing to ai-book-cover-generator

Thanks for wanting to push covers. This is a hobbyist open-source project
and PRs are welcome — bug fixes, new backends, prompt presets, layout
templates, whatever you've got.

## Dev setup

```bash
git clone https://github.com/<you>/ai-book-cover-generator.git
cd ai-book-cover-generator
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
python -m covergen --help
```

The desktop entry point is `python -m covergen`. The GUI is Tkinter-based
and ships with the standard library, so no extra runtime is required for
the shell itself. Generation backends (Stable Diffusion, SDXL, custom
ONNX) are optional extras — see `pyproject.toml`.

## Branching

- `main` — stable, releasable.
- `dev` — integration branch, PRs land here first.
- `feat/<short-name>` — one feature per branch.

## Commit style

Conventional-ish. `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`.
Keep the subject under 72 chars.

## Adding a generation backend

1. Drop a new module in `covergen/services/backends/`.
2. Subclass `BaseBackend` from `covergen.services.backends.base`.
3. Register it in `covergen/services/backends/registry.py`.
4. Add a config block in `covergen/config/default.yaml`.
5. Add a test in `tests/`.

## Adding a prompt preset

Presets live in `covergen/models/presets/`. One YAML per genre. The loader
in `covergen/models/preset_loader.py` picks them up automatically.

## Code style

- `ruff` for lint, `black` for format, `mypy --strict` on `covergen/`.
- Type hints required on public functions.
- No bare `except:`. Log and re-raise or handle.

## Testing

```bash
pytest -q
pytest --cov=covergen tests/
```

CI runs on Windows + Linux, Python 3.11 and 3.12.

## Reporting bugs

Open an issue with: OS, Python version, backend (SD/SDXL/ONNX), and the
full traceback. If it's a generation artifact, attach the seed and prompt.