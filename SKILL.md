---
name: serial-power-ctl
description: 使用 serialwrite.py 通过一个串口查询或控制四路继电器的开关状态。
---

# 四路串口电源控制

在本文件所在目录运行 `serialwrite.py`。运行环境需要 Python 3.8+ 和 pyserial。

一个串口对应 4 个独立通道：`1`、`2`、`3`、`4`。通过以下必填参数指定操作：

- `--port`：实际串口路径，例如 `/dev/ttyUSB1`。
- `--channel`：通道号，可用空格指定多个，例如 `1 2 3 4`；多个通道依次操作。
- `--action`：`status` 查询当前状态，`on` 上电，`off` 断电。

执行 `on` / `off` 前，建议先用 `status` 查看目标通道当前状态；操作后可再次查询确认。查询不会改变开关状态，仅查询时不要发送开关命令。

```bash
# 查询全部四路
python3 serialwrite.py --port /dev/ttyUSB1 --channel 1 2 3 4 --action status

# 第 4 路上电
python3 serialwrite.py --port /dev/ttyUSB1 --channel 4 --action on

# 查询第 4 路状态
python3 serialwrite.py --port /dev/ttyUSB1 --channel 4 --action status

# 第 4 路断电
python3 serialwrite.py --port /dev/ttyUSB1 --channel 4 --action off
```

每次运行完成后退出。只操作用户指定的通道，查询结果以实时返回为准。
