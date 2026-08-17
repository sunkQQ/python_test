#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tail4Win - Windows版本的实时日志文件监控工具

@author sunk
@since 2026-06-10
"""

import os
import sys
import time
import argparse
import re
from pathlib import Path
from typing import Optional, List, Callable
from datetime import datetime


class Tail4Win:
    """实时日志文件监控类"""

    def __init__(
        self,
        file_path: str,
        lines: int = 10,
        follow: bool = True,
        filter_pattern: Optional[str] = None,
        highlight: Optional[str] = None,
    ):
        """
        初始化Tail4Win

        :param file_path: 要监控的文件路径
        :param lines: 初始显示的行数
        :param follow: 是否持续监控文件变化
        :param filter_pattern: 过滤正则表达式
        :param highlight: 高亮正则表达式
        """
        self.file_path = Path(file_path)
        self.lines = lines
        self.follow = follow
        self.filter_pattern = re.compile(filter_pattern) if filter_pattern else None
        self.highlight_pattern = re.compile(highlight) if highlight else None
        self.last_size = 0
        self.last_inode = None

        # 颜色代码
        self.colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "magenta": "\033[95m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "reset": "\033[0m",
            "bold": "\033[1m",
        }

    def validate_file(self) -> bool:
        """验证文件是否存在且可读"""
        if not self.file_path.exists():
            print(f"错误: 文件 '{self.file_path}' 不存在", file=sys.stderr)
            return False

        if not self.file_path.is_file():
            print(f"错误: '{self.file_path}' 不是文件", file=sys.stderr)
            return False

        return True

    def get_file_size(self) -> int:
        """获取文件大小"""
        try:
            return self.file_path.stat().st_size
        except (OSError, FileNotFoundError):
            return 0

    def read_last_lines(self, count: int) -> List[str]:
        """
        读取文件的最后N行

        :param count: 要读取的行数
        :return: 行列表
        """
        try:
            with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
                # 读取所有行并返回最后N行
                lines = f.readlines()
                return lines[-count:] if count > 0 else lines
        except Exception as e:
            print(f"读取文件时出错: {e}", file=sys.stderr)
            return []

    def apply_filter(self, line: str) -> bool:
        """应用过滤规则"""
        if self.filter_pattern:
            return bool(self.filter_pattern.search(line))
        return True

    def apply_highlight(self, line: str) -> str:
        """应用高亮规则"""
        if self.highlight_pattern:
            return self.highlight_pattern.sub(
                f"{self.colors['yellow']}\\g<0>{self.colors['reset']}", line
            )
        return line

    def format_line(self, line: str, line_number: int) -> str:
        """
        格式化输出行

        :param line: 原始行内容
        :param line_number: 行号
        :return: 格式化后的行
        """
        # 添加行号
        formatted = f"{self.colors['cyan']}{line_number:6d}{self.colors['reset']} | "

        # 应用高亮
        highlighted = self.apply_highlight(line.rstrip())

        return formatted + highlighted

    def display_lines(self, lines: List[str], start_line: int = 1):
        """
        显示行内容

        :param lines: 要显示的行列表
        :param start_line: 起始行号
        """
        for i, line in enumerate(lines, start=start_line):
            if self.apply_filter(line):
                print(self.format_line(line, i), end="\n")

    def check_file_rotation(self) -> bool:
        """检查文件是否被轮转（重新创建）"""
        try:
            current_size = self.get_file_size()

            # 如果文件变小了，可能是被轮转了
            if current_size < self.last_size:
                self.last_size = 0
                print(
                    f"\n{self.colors['yellow']}文件可能已被轮转{self.colors['reset']}"
                )
                return True

            return False
        except Exception:
            return False

    def follow_file(self):
        """持续监控文件变化"""
        print(
            f"{self.colors['green']}开始监控文件: {self.file_path}{self.colors['reset']}"
        )
        print(f"{self.colors['green']}按 Ctrl+C 退出{self.colors['reset']}\n")

        try:
            while self.follow:
                time.sleep(0.1)  # 减少CPU使用率

                # 检查文件轮转
                if self.check_file_rotation():
                    continue

                current_size = self.get_file_size()

                # 如果文件有新内容
                if current_size > self.last_size:
                    try:
                        with open(
                            self.file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            f.seek(self.last_size)
                            new_lines = f.readlines()

                            if new_lines:
                                # 计算新的行号（简化处理，实际应该统计总行数）
                                self.display_lines(new_lines)

                            self.last_size = current_size
                    except Exception as e:
                        print(f"读取新内容时出错: {e}", file=sys.stderr)

        except KeyboardInterrupt:
            print(f"\n{self.colors['yellow']}监控已停止{self.colors['reset']}")

    def run(self):
        """运行tail4win"""
        if not self.validate_file():
            return 1

        # 显示初始内容
        initial_lines = self.read_last_lines(self.lines)
        if initial_lines:
            print(
                f"{self.colors['bold']}最后 {len(initial_lines)} 行:{self.colors['reset']}"
            )
            self.display_lines(initial_lines)
            print()

        # 更新文件大小
        self.last_size = self.get_file_size()

        # 持续监控
        if self.follow:
            self.follow_file()

        return 0


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Tail4Win - Windows版本的实时日志文件监控工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  tail4win.py log.txt                    # 显示最后10行并持续监控
  tail4win.py -n 50 log.txt              # 显示最后50行
  tail4win.py -f error.log               # 持续监控文件
  tail4win.py -p "ERROR" log.txt         # 只显示包含ERROR的行
  tail4win.py -h "\\d{4}-\\d{2}-\\d{2}" log.txt  # 高亮日期
        """,
    )

    parser.add_argument("file", help="要监控的日志文件路径")

    parser.add_argument(
        "-n", "--lines", type=int, default=10, help="初始显示的行数 (默认: 10)"
    )

    parser.add_argument(
        "-f",
        "--follow",
        action="store_true",
        default=True,
        help="持续监控文件变化 (默认: True)",
    )

    parser.add_argument(
        "--no-follow", action="store_false", dest="follow", help="不持续监控文件变化"
    )

    parser.add_argument("-p", "--pattern", help="只显示匹配正则表达式的行")

    parser.add_argument("-H", "--highlight", help="高亮匹配正则表达式的内容")

    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()

    tail = Tail4Win(
        file_path=args.file,
        lines=args.lines,
        follow=args.follow,
        filter_pattern=args.pattern,
        highlight=args.highlight,
    )

    sys.exit(tail.run())


if __name__ == "__main__":
    main()
