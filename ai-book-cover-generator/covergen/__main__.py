"""Bootstrap entry point for the covergen desktop tool.

Wires config -> backend registry -> GUI shell. Falls back to a headless
CLI render when ``--cli`` is passed or when Tk is unavailable.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from covergen.config.loader import load_config
from covergen.services.backends.registry import build_backend
from covergen.utils.logging import configure_logging
from covergen.utils.paths import ensure_project_dirs


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="covergen", description="AI book cover generator")
    parser.add_argument("--config", type=Path, default=None, help="path to config yaml")
    parser.add_argument("--cli", action="store_true", help="run headless, no GUI")
    parser.add_argument("--prompt", type=str, default=None, help="prompt for CLI render")
    parser.add_argument("--out", type=Path, default=Path("outputs"), help="output directory")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    configure_logging(verbose=args.verbose)
    log = logging.getLogger("covergen")

    config = load_config(args.config)
    ensure_project_dirs(config)

    backend = build_backend(config)

    if args.cli or not args.prompt:
        if not args.prompt:
            log.error("no --prompt supplied for CLI render")
            return 2
        from covergen.handlers.cli_render import run_cli_render

        return run_cli_render(config, backend, prompt=args.prompt, out_dir=args.out, seed=args.seed)

    from covergen.handlers.gui_app import launch_gui

    launch_gui(config, backend)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())