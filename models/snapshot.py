from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass
class SensorSnapshot:
    temperature_c: float | None
    ph: float
    turbidity: float
    ph_voltage: float
    turbidity_voltage: float

    def to_json(self) -> str:
        payload = {
            "ph": round(self.ph, 3),
            "turb": round(self.turbidity, 3),
            "ph_voltage": round(self.ph_voltage, 5),
            "turb_voltage": round(self.turbidity_voltage, 5),
        }
        payload["temp"] = None if self.temperature_c is None else round(self.temperature_c, 1)
        return json.dumps(payload, ensure_ascii=False)
