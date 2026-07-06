from __future__ import annotations

import time

from config import AnalogFormula


class AnalogSensorReader:
    def __init__(self, adc, sample_delay_s: float) -> None:
        self.adc = adc
        self.sample_delay_s = sample_delay_s

    def read_formula_value(self, channel: int, sample_count: int, formula: AnalogFormula) -> tuple[float, float]:
        voltage_total = 0.0

        for _ in range(sample_count):
            voltage_total += self.adc.read_voltage(channel)
            time.sleep(self.sample_delay_s)

        average_voltage = voltage_total / sample_count
        value = formula.slope * average_voltage + formula.intercept
        value = (value + formula.offset) * formula.scale

        if formula.min_value is not None and value < formula.min_value:
            value = formula.min_value
        if formula.max_value is not None and value > formula.max_value:
            value = formula.max_value

        return value, average_voltage
