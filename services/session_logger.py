from __future__ import annotations

from datetime import datetime
from pathlib import Path


class SessionLogger:
    def __init__(self, base_dir: str) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.file_path: Path | None = None

    def start_session(self) -> Path:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.file_path = self.base_dir / f"{timestamp}.jsonl"
        self.file_path.touch()
        return self.file_path

    def write_line(self, line: str) -> None:
        if self.file_path is None:
            raise RuntimeError("Session logger has not been started")
        with self.file_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
