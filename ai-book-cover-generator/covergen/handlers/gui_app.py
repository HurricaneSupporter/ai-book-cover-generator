"""Tkinter desktop shell for covergen.

Single-window form: title, author, genre, seed, backend name, render
button. Rendering runs on a worker thread so the UI never freezes; the
result is posted back via a queue polled with ``after``.
"""
from __future__ import annotations

import logging
import queue
import threading
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, StringVar, Tk, filedialog, messagebox
from tkinter import ttk

from covergen.config.schema import AppConfig
from covergen.core.pipeline import CoverJob, CoverResult, run_pipeline
from covergen.models.preset_loader import list_genres
from covergen.services.backends.base import BaseBackend

log = logging.getLogger(__name__)


def launch_gui(config: AppConfig, backend: BaseBackend) -> None:
    app = CovergenApp(config, backend)
    app.run()


class CovergenApp:
    def __init__(self, config: AppConfig, backend: BaseBackend) -> None:
        self.config = config
        self.backend = backend
        self.root = Tk()
        self.root.title(f"covergen {backend.name}")
        self.root.geometry("720x560")
        self._results: queue.Queue[CoverResult | Exception] = queue.Queue()
        self._build_widgets()

    def _build_widgets(self) -> None:
        frm = ttk.Frame(self.root, padding=16)
        frm.pack(fill=BOTH, expand=True)

        ttk.Label(frm, text="Title").pack(anchor="w")
        self.title_var = StringVar(value="The Cartographer's Lantern")
        ttk.Entry(frm, textvariable=self.title_var).pack(fill="x")

        ttk.Label(frm, text="Author").pack(anchor="w", pady=(10, 0))
        self.author_var = StringVar(value="A. M. Reyes")
        ttk.Entry(frm, textvariable=self.author_var).pack(fill="x")

        ttk.Label(frm, text="Genre").pack(anchor="w", pady=(10, 0))
        self.genre_var = StringVar(value=self.config.prompt.genre)
        ttk.Combobox(
            frm, textvariable=self.genre_var, values=list_genres(self.config.prompt.preset_dir)
        ).pack(fill="x")

        ttk.Label(frm, text="Seed (blank = random)").pack(anchor="w", pady=(10, 0))
        self.seed_var = StringVar(value="")
        ttk.Entry(frm, textvariable=self.seed_var).pack(fill="x")

        self.status_var = StringVar(value="idle")
        ttk.Label(frm, textvariable=self.status_var).pack(anchor="w", pady=(16, 0))

        row = ttk.Frame(frm)
        row.pack(fill="x", pady=(16, 0))
        ttk.Button(row, text="Render cover", command=self._on_render).pack(side=LEFT)
        ttk.Button(row, text="Open output folder", command=self._open_output).pack(side=RIGHT)

    def _on_render(self) -> None:
        try:
            seed = int(self.seed_var.get()) if self.seed_var.get().strip() else None
        except ValueError:
            messagebox.showerror("covergen", "seed must be an integer")
            return

        job = CoverJob(
            title=self.title_var.get().strip() or "Untitled",
            author=self.author_var.get().strip() or "Anonymous",
            genre=self.genre_var.get().strip() or self.config.prompt.genre,
            seed=seed,
        )
        self.status_var.set("rendering…")
        threading.Thread(target=self._worker, args=(job,), daemon=True).start()
        self.root.after(200, self._poll)

    def _worker(self, job: CoverJob) -> None:
        try:
            self._results.put(run_pipeline(self.config, self.backend, job))
        except Exception as exc:  # surfaced in the UI thread
            log.exception("render failed")
            self._results.put(exc)

    def _poll(self) -> None:
        try:
            item = self._results.get_nowait()
        except queue.Empty:
            self.root.after(200, self._poll)
            return
        if isinstance(item, Exception):
            self.status_var.set(f"failed: {item}")
            messagebox.showerror("covergen", f"render failed:\n{item}")
        else:
            self.status_var.set(f"done in {item.elapsed_ms}ms -> {item.cover_path.name}")
        self.root.after(200, self._poll)

    def _open_output(self) -> None:
        import os
        import subprocess

        out = self.config.output_dir.resolve()
        out.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            subprocess.Popen(["explorer", str(out)])
        else:
            subprocess.Popen(["xdg-open", str(out)])

    def run(self) -> None:
        self.root.mainloop()