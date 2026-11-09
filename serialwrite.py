#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过一个串口控制四路继电器，每次执行一次指定的开关或状态查询操作。"""

import argparse
import sys


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("必须是正整数")
    return number


def positive_timeout(value):
    number = float(value)
    if not 0 < number < float("inf"):
        raise argparse.ArgumentTypeError("必须是有限的正数")
    return number


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True, help="串口，例如 /dev/ttyUSB0")
    parser.add_argument("--baudrate", type=positive_int, default=9600,
                        help="波特率（默认：9600）")
    parser.add_argument("--channel", type=int, nargs="+", choices=(1, 2, 3, 4),
                        required=True, help="通道号，可指定多个，例如 --channel 1 2 3 4")
    parser.add_argument("--action", choices=("on", "off", "status"), required=True,
                        help="on 打开，off 关闭，status 查询当前状态（不改变开关）")
    parser.add_argument("--feedback", action="store_true",
                        help="开关操作请求并校验状态反馈（默认不反馈；status 始终读取反馈）")
    parser.add_argument("--timeout", type=positive_timeout, default=0.5,
                        help="读取和写入超时，单位秒（默认：0.5）")
    return parser.parse_args(argv)


def make_command(channel, action, feedback=False):
    operation = {"off": 0x00, "on": 0x01, "status": 0x05}[action]
    if feedback and action != "status":
        operation += 2
    return bytes((0xA0, channel, operation, 0xA0 + channel + operation))


def check_feedback(response, channel, action):
    if len(response) != 4:
        raise ValueError("第 {} 路反馈不完整：期望 4 字节，收到 {} 字节 ({})".format(
            channel, len(response), response.hex(" ") or "无数据"))
    start, address, state, checksum = response
    if (start != 0xA0 or address != channel or state not in (0, 1)
            or checksum != ((start + address + state) & 0xFF)):
        raise ValueError("第 {} 路反馈格式或校验错误：{}".format(channel, response.hex(" ")))
    if action != "status":
        expected = 1 if action == "on" else 0
        if state != expected:
            raise ValueError("第 {} 路反馈状态与请求不一致：{}".format(channel, response.hex(" ")))
    return state


def main(argv=None):
    args = parse_args(argv)
    read_feedback = args.feedback or args.action == "status"
    try:
        import serial
    except ImportError:
        print("错误：缺少 pyserial 依赖，请在具备该依赖的 Python 环境中运行。", file=sys.stderr)
        return 1

    try:
        with serial.Serial(args.port, args.baudrate, timeout=args.timeout,
                           write_timeout=args.timeout) as connection:
            if read_feedback:
                connection.reset_input_buffer()
            for channel in dict.fromkeys(args.channel):
                command = make_command(channel, args.action, args.feedback)
                if connection.write(command) != len(command):
                    raise ValueError("第 {} 路命令未完整写入串口".format(channel))
                connection.flush()
                if read_feedback:
                    response = connection.read(4)
                    state = check_feedback(response, channel, args.action)
                    if args.action == "status":
                        result = "当前状态：打开" if state else "当前状态：关闭"
                    else:
                        result = "反馈确认已打开" if state else "反馈确认已关闭"
                else:
                    result = "已发送打开命令（不反馈）" if args.action == "on" else "已发送关闭命令（不反馈）"
                print("第 {} 路：{}，发送 {}".format(channel, result, command.hex(" ").upper()))
    except (serial.SerialException, OSError, ValueError) as error:
        print("错误：{}".format(error), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("操作已中断。", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
