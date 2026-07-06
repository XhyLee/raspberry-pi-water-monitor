from __future__ import annotations

import time

from smbus2 import SMBus


class ADS1115:
    CONVERSION_REGISTER = 0x00
    CONFIG_REGISTER = 0x01

    MUX_BY_CHANNEL = {
        0: 0x4000,
        1: 0x5000,
        2: 0x6000,
        3: 0x7000,
    }

    GAIN_BY_SETTING = {
        2 / 3: (0x0000, 6.144),
        1: (0x0200, 4.096),
        2: (0x0400, 2.048),
        4: (0x0600, 1.024),
        8: (0x0800, 0.512),
        16: (0x0A00, 0.256),
    }

    DATA_RATE_BITS = {
        8: 0x0000,
        16: 0x0020,
        32: 0x0040,
        64: 0x0060,
        128: 0x0080,
        250: 0x00A0,
        475: 0x00C0,
        860: 0x00E0,
    }

    def __init__(self, bus_id: int, address: int = 0x48, gain: float = 1, data_rate: int = 860) -> None:
        if gain not in self.GAIN_BY_SETTING:
            raise ValueError(f"Unsupported ADS1115 gain: {gain}")
        if data_rate not in self.DATA_RATE_BITS:
            raise ValueError(f"Unsupported ADS1115 data rate: {data_rate}")

        self.address = address
        self.data_rate = data_rate
        self._gain_bits, self._full_scale_voltage = self.GAIN_BY_SETTING[gain]
        self._data_rate_bits = self.DATA_RATE_BITS[data_rate]
        self._bus = SMBus(bus_id)

    def read_raw(self, channel: int) -> int:
        if channel not in self.MUX_BY_CHANNEL:
            raise ValueError(f"ADS1115 channel must be 0-3, got {channel}")

        config = (
            0x8000
            | self.MUX_BY_CHANNEL[channel]
            | self._gain_bits
            | 0x0100
            | self._data_rate_bits
            | 0x0003
        )
        self._write_register(self.CONFIG_REGISTER, config)
        time.sleep(1.0 / self.data_rate + 0.002)

        raw = self._read_register(self.CONVERSION_REGISTER)
        if raw & 0x8000:
            raw -= 1 << 16
        return raw

    def read_voltage(self, channel: int) -> float:
        raw = self.read_raw(channel)
        return raw * (self._full_scale_voltage / 32768.0)

    def close(self) -> None:
        self._bus.close()

    def _write_register(self, register: int, value: int) -> None:
        payload = [(value >> 8) & 0xFF, value & 0xFF]
        self._bus.write_i2c_block_data(self.address, register, payload)

    def _read_register(self, register: int) -> int:
        data = self._bus.read_i2c_block_data(self.address, register, 2)
        return (data[0] << 8) | data[1]

