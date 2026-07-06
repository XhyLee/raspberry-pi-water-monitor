from dataclasses import dataclass


I2C_BUS = 1

ADS1115_ADDRESS = 0x48
ADS1115_GAIN = 1
ADS1115_DATA_RATE = 860

OLED_ADDRESS = 0x3C
OLED_WIDTH = 128
OLED_HEIGHT = 64
DISPLAY_LINE_HEIGHT = 16
OLED_FONT_CANDIDATES = [
    "./assets/msyh.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
OLED_FONT_SIZE = 12

LOOP_DELAY_S = 0.2
RAW_PRINT_INTERVAL_S = 1.0

DS18B20_BASE_DIR = "/sys/bus/w1/devices"
DS18B20_FAMILY_PREFIX = "28-"
DATA_DIR = "date"

PH_CHANNEL = 0
TURBIDITY_CHANNEL = 1

PH_READ_TIMES = 10
TURBIDITY_READ_TIMES = 10
SAMPLE_DELAY_S = 0.005


@dataclass(frozen=True)
class AnalogFormula:
    slope: float
    intercept: float
    min_value: float | None = None
    max_value: float | None = None
    offset: float = 0.0
    scale: float = 1.0


PH_FORMULA = AnalogFormula(
    slope=-5.7541,
    intercept=16.654,
    min_value=0.0,
    max_value=14.0,
    offset=0.0,
    scale=1.0,
)

TURBIDITY_FORMULA = AnalogFormula(
    slope=-865.68,
    intercept=2047.19,
    min_value=0.0,
    offset=0.0,
    scale=1.0,
)
