# serial-power-ctl
Control outlet power via serial commands to onboard relays.

通过同一个串口独立控制四路继电器。运行环境需要 Python 3.8+、pyserial，以及设备对应的串口驱动。

每次运行执行一次开关或状态查询操作后退出。多个通道按参数顺序依次操作；重复通道只执行一次。

串口、通道和操作必须分别通过 `--port`、`--channel`、`--action` 指定。波特率默认 `9600`、超时默认 `0.5` 秒，开关操作默认不请求反馈，与原 demo 一致。状态查询始终读取并校验反馈，无需添加 `--feedback`，也不会改变开关状态。

```bash
# 打开第 1 路，默认不请求反馈，与原 demo 一致
python3 serialwrite.py --port /dev/ttyUSB0 --channel 1 --action on

# 关闭第 4 路，并读取、校验状态反馈
python3 serialwrite.py --port /dev/ttyUSB0 --channel 4 --action off --feedback

# 依次打开全部四路
python3 serialwrite.py --port /dev/ttyUSB0 --channel 1 2 3 4 --action on

# 查询第 1 路当前状态
python3 serialwrite.py --port /dev/ttyUSB1 --channel 1 --action status

# 依次查询全部四路当前状态
python3 serialwrite.py --port /dev/ttyUSB1 --channel 1 2 3 4 --action status

# Windows 串口及可选通信参数
python serialwrite.py --port COM12 --baudrate 9600 --timeout 1 --channel 2 --action off

# 查看全部参数
python3 serialwrite.py --help
```

| 参数 | 含义 | 默认值 |
| --- | --- | --- |
| `--port` | 串口设备 | 必填 |
| `--channel` | 一个或多个通道，范围 1～4 | 必填 |
| `--action` | `on` 打开，`off` 关闭，`status` 查询当前状态 | 必填 |
| `--baudrate` | 波特率，正整数 | `9600` |
| `--feedback` | 开关操作请求并校验四字节状态反馈；查询自动读取反馈 | 开关操作不反馈 |
| `--timeout` | 串口读取和写入超时，单位秒，有限正数 | `0.5` |

开关操作不反馈时仅表示命令已发送；启用反馈或查询状态时，脚本检查反馈长度、起始字节、通道、状态及校验和。查询输出各通道的“当前状态：打开”或“当前状态：关闭”。反馈表示模块报告的开关状态，不代表外部设备实际通电或正常工作。
通信或反馈异常时停止后续操作并以非零状态退出，已执行的通道不会回滚。
