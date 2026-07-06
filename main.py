from __future__ import annotations

import threading
import time

import config
from drivers.ads1115 import ADS1115
from drivers.oled_ssd1306 import SSD1306OLED
from models.snapshot import SensorSnapshot
from services.analog_sensors import AnalogSensorReader
from services.session_logger import SessionLogger
from services.temperature import DS18B20Reader


class WaterMonitorApp:
    def __init__(self) -> None:
        self.ads = ADS1115(
            bus_id=config.I2C_BUS,
            address=config.ADS1115_ADDRESS,
            gain=config.ADS1115_GAIN,
            data_rate=config.ADS1115_DATA_RATE,
        )
        self.oled = SSD1306OLED(
            bus_id=config.I2C_BUS,
            address=config.OLED_ADDRESS,
            width=config.OLED_WIDTH,
            height=config.OLED_HEIGHT,
            font_candidates=config.OLED_FONT_CANDIDATES,
            font_size=config.OLED_FONT_SIZE,
            line_height=config.DISPLAY_LINE_HEIGHT,
        )
        self.temperature_reader = DS18B20Reader(
            base_dir=config.DS18B20_BASE_DIR,
            family_prefix=config.DS18B20_FAMILY_PREFIX,
        )
        self.analog_reader = AnalogSensorReader(
            adc=self.ads,
            sample_delay_s=config.SAMPLE_DELAY_S,
        )
        self.logger = SessionLogger(config.DATA_DIR)
        self.current_page = 0
        self.last_console_print_time = 0.0
        self.stop_requested = False

    def setup(self) -> None:
        self.oled.init()
        self.show_idle_screen()
        time.sleep(1.0)

    def run_measurement_loop(self) -> None:
        self.stop_requested = False
        log_file = self.logger.start_session()
        print(f"数据将保存到: {log_file}")
        try:
            while not self.stop_requested:
                snapshot = self.read_snapshot()
                self.render(snapshot)
                self.print_snapshot(snapshot)
                self.logger.write_line(snapshot.to_json())
                time.sleep(config.LOOP_DELAY_S)
        except KeyboardInterrupt:
            pass
        finally:
            self.show_stopped_screen()

    def read_snapshot(self) -> SensorSnapshot:
        try:
            temperature_c = self.temperature_reader.read_celsius()
        except Exception:
            temperature_c = None

        ph, ph_voltage = self.analog_reader.read_formula_value(
            channel=config.PH_CHANNEL,
            sample_count=config.PH_READ_TIMES,
            formula=config.PH_FORMULA,
        )
        turbidity, turbidity_voltage = self.analog_reader.read_formula_value(
            channel=config.TURBIDITY_CHANNEL,
            sample_count=config.TURBIDITY_READ_TIMES,
            formula=config.TURBIDITY_FORMULA,
        )
        return SensorSnapshot(
            temperature_c=temperature_c,
            ph=ph,
            turbidity=turbidity,
            ph_voltage=ph_voltage,
            turbidity_voltage=turbidity_voltage,
        )

    def render(self, snapshot: SensorSnapshot) -> None:
        if self.current_page == 0:
            temperature_text = "未连接 Missing" if snapshot.temperature_c is None else f"{snapshot.temperature_c:>5.1f} C"
            self.oled.show_lines(
                [
                    "温度 Temp",
                    temperature_text,
                    "按 u/d 翻页",
                    "u/d switch",
                ]
            )
            return

        if self.current_page == 1:
            self.oled.show_lines(
                [
                    "酸碱 pH",
                    f"{snapshot.ph:>7.3f}",
                    f"电压 V {snapshot.ph_voltage:>6.4f}",
                    "u/d switch",
                ]
            )
            return

        self.oled.show_lines(
            [
                "浊度 Turb",
                f"{snapshot.turbidity:>6.2f}",
                f"电压 V {snapshot.turbidity_voltage:>4.2f}",
                "u/d switch",
            ]
        )

    def print_snapshot(self, snapshot: SensorSnapshot) -> None:
        now = time.monotonic()
        if now - self.last_console_print_time >= config.RAW_PRINT_INTERVAL_S:
            print(snapshot.to_json(), flush=True)
            self.last_console_print_time = now

    def show_idle_screen(self) -> None:
        self.oled.show_lines(
            [
                "系统开机 Boot",
                "输入 s 开始",
                "Type s to start",
                "exit 退出",
            ]
        )

    def show_stopped_screen(self) -> None:
        self.oled.show_lines(
            [
                "停止测试 Stop",
                "输入 s 重测",
                "Type exit 退出",
                "",
            ]
        )

    def show_exit_screen(self) -> None:
        self.oled.show_lines(
            [
                "系统退出 Exit",
                "OLED 熄灭",
                "Powering off",
                "",
            ]
        )

    def page_up(self) -> None:
        self.current_page = (self.current_page - 1) % 3

    def page_down(self) -> None:
        self.current_page = (self.current_page + 1) % 3

    def request_stop(self) -> None:
        self.stop_requested = True

    def shutdown(self) -> None:
        self.oled.power_off()
        self.oled.close()
        self.ads.close()


def run_with_keyboard_paging(app: WaterMonitorApp) -> None:
    worker = threading.Thread(target=app.run_measurement_loop, daemon=True)
    worker.start()
    try:
        while worker.is_alive():
            command = input("测试中输入 u/d 翻页, stop 停止: ").strip().lower()
            if command == "u":
                app.page_up()
            elif command == "d":
                app.page_down()
            elif command == "stop":
                app.request_stop()
            else:
                print("无效命令，请输入 u、d 或 stop。")
    except KeyboardInterrupt:
        app.request_stop()
    finally:
        worker.join()


def command_loop(app: WaterMonitorApp) -> None:
    while True:
        command = input("请输入命令 / Command [s/exit]: ").strip().lower()
        if command == "s":
            print("开始测试，Ctrl+C 或 stop 可停止，u/d 可翻页。")
            app.current_page = 0
            run_with_keyboard_paging(app)
            continue

        if command == "exit":
            app.show_exit_screen()
            time.sleep(1.0)
            break

        print("无效命令，请输入 s 或 exit。")


def main() -> None:
    app = WaterMonitorApp()
    app.setup()
    try:
        command_loop(app)
    finally:
        app.shutdown()


if __name__ == "__main__":
    main()
