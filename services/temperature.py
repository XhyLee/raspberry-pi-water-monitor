from __future__ import annotations

from pathlib import Path


class DS18B20Reader:
    def __init__(self, base_dir: str, family_prefix: str = "28-") -> None:
        self.base_path = Path(base_dir)
        self.family_prefix = family_prefix

    def read_celsius(self) -> float:
        sensor_file = self._resolve_sensor_file()
        lines = sensor_file.read_text(encoding="utf-8").strip().splitlines()
        if len(lines) < 2:
            raise RuntimeError("DS18B20 returned incomplete data")
        if not lines[0].strip().endswith("YES"):
            raise RuntimeError("DS18B20 CRC check failed")

        marker = "t="
        position = lines[1].find(marker)
        if position == -1:
            raise RuntimeError("DS18B20 temperature field not found")

        milli_celsius = int(lines[1][position + len(marker) :])
        return milli_celsius / 1000.0

    def _resolve_sensor_file(self) -> Path:
        for path in self.base_path.iterdir():
            if path.is_dir() and path.name.startswith(self.family_prefix):
                sensor_file = path / "w1_slave"
                if sensor_file.exists():
                    return sensor_file
        raise FileNotFoundError("No DS18B20 sensor found in /sys/bus/w1/devices")

