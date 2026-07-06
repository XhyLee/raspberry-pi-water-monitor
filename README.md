# Raspberry Pi 4B Water Monitor

这个目录是当前硬件版本的 Raspberry Pi 4B Python 工程。

## 当前硬件

- Raspberry Pi 4B
- ADS1115 16-bit ADC
- pH 模块
- 浊度模块
- DS18B20 温度传感器
- I2C OLED 屏幕

## 当前功能

- 实时采集温度、pH、浊度
- OLED 中英双语显示
- 控制台输入 `s` 开始测试
- 测试中输入 `u` 上一页，输入 `d` 下一页
- 测试中输入 `stop` 或按 `Ctrl+C` 停止测试
- 控制台输入 `exit` 退出系统并熄灭 OLED
- 控制台持续输出 JSON 数据和原始电压
- 每次测试数据保存到 `date` 文件夹，文件名为日期加时间

## 目录结构

- `main.py`: 程序入口和交互流程
- `config.py`: 参数、校准配置、字体候选
- `requirements.txt`: Python 依赖
- `drivers/ads1115.py`: ADS1115 驱动
- `drivers/oled_ssd1306.py`: OLED 驱动
- `services/temperature.py`: DS18B20 读取
- `services/analog_sensors.py`: pH 和浊度读取/换算
- `models/snapshot.py`: 采样数据模型

## 运行方式

```bash
cd ~/pi
source .venv/bin/activate
python main.py
```

启动后：

- OLED 显示系统待机页面
- 输入 `s` 开始测试
- 测试中输入 `u/d` 控制翻页
- 输入 `stop` 或按 `Ctrl+C` 停止测试并回到停止页面
- 输入 `exit` 退出并关闭 OLED

## 校准说明

当前 pH 和浊度仍保留原 STM32 版本公式，同时加入了更方便后续校准的参数：

- `config.py -> PH_FORMULA`
- `config.py -> TURBIDITY_FORMULA`

可以调的字段：

- `slope`
- `intercept`
- `offset`
- `scale`

程序输出 JSON 时还会带：

- `ph_voltage`
- `turb_voltage`

这样你可以拿标准液或已知样本边测边改参数。

## pH 数值长时间不变的排查结论

这次远程检查时，`ADS1115 A0` 这一路的原始值基本稳定在同一小范围，而 `A1` 浊度通道是会变化的。

这说明：

- 程序本身在持续刷新
- ADS1115 也在正常工作
- pH 显示看起来不变，主要原因更可能是 `pH 模块输出电压本身几乎不变`

更常见的原因有：

- pH 探头还没充分浸泡和活化
- pH 模块的 `AO` 没接对，接到了固定电平脚
- pH 模块没有和树莓派/ADS1115 共地
- pH 模块上的电位器/增益还没调好
- 探头一直处在同一种液体里，本来就不会明显变化

当前代码已经把 pH 显示精度提高到 3 位小数，并把电压显示精度提高了，方便你观察微小变化。

## 接线

### OLED 与 ADS1115 共用 I2C

- 树莓派 `Pin 3(GPIO2 SDA1)` -> OLED `SDA`
- 树莓派 `Pin 5(GPIO3 SCL1)` -> OLED `SCL`
- 树莓派 `Pin 1(3.3V)` -> OLED `VCC`
- 树莓派 `Pin 6(GND)` -> OLED `GND`

- 树莓派 `Pin 3(GPIO2 SDA1)` -> ADS1115 `SDA`
- 树莓派 `Pin 5(GPIO3 SCL1)` -> ADS1115 `SCL`
- 树莓派 `Pin 1(3.3V)` -> ADS1115 `VDD`
- 树莓派 `Pin 6(GND)` -> ADS1115 `GND`
- ADS1115 `ADDR` -> `GND`

### ADS1115 模拟输入

- `A0` -> pH 模块模拟输出
- `A1` -> 浊度模块模拟输出

### DS18B20

- 树莓派 `Pin 7(GPIO4)` -> `DQ`
- 树莓派 `Pin 1(3.3V)` -> `VCC`
- 树莓派 `Pin 6(GND)` -> `GND`
- `DQ` 和 `3.3V` 之间加 `4.7kΩ` 电阻
