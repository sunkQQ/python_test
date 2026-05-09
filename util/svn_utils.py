#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SVN操作工具 - 获取分支、提交注释和人员信息

功能说明：
- 列出SVN仓库的分支结构
- 获取提交历史记录（包含注释和提交人员）
- 获取最初的提交记录
- 支持拉取代码到本地

使用方法：
1. 查看帮助：python svn_utils.py --help
2. 列出分支：python svn_utils.py --list-branches <repo_url>
3. 获取提交历史：python svn_utils.py --log <repo_url>
4. 获取最初提交：python svn_utils.py --first-log <repo_url>
5. 拉取代码：python svn_utils.py --checkout <repo_url> <local_path>

注意事项：
- 需要安装SVN客户端（TortoiseSVN或命令行SVN）
- 确保网络能访问SVN仓库

@author: sunk
@since: 2026-05-09
"""

import subprocess
import sys
import argparse
import re


class SVNUtils:
    """
    SVN操作工具类

    核心功能：
    - 执行SVN命令
    - 列出分支
    - 获取提交日志
    - 拉取代码
    """

    def __init__(self):
        """初始化工具"""
        self.svn_cmd = "svn"  # SVN命令路径

    def _run_command(self, cmd_args):
        """
        执行SVN命令

        :param cmd_args: 命令参数列表
        :return: (stdout, stderr, return_code)
        """
        try:
            result = subprocess.run(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                errors="replace",
            )
            return result.stdout, result.stderr, result.returncode
        except FileNotFoundError:
            print("❌ 未找到SVN命令，请确保已安装SVN客户端")
            return "", "SVN command not found", 1
        except Exception as e:
            return "", str(e), 1

    def list_branches(self, repo_url):
        """
        列出SVN仓库的分支结构

        :param repo_url: SVN仓库URL
        :return: 分支列表
        """
        # print(f"🔍 正在获取 {repo_url} 的分支结构...")

        # 尝试标准的SVN目录结构
        branches_url = f"{repo_url}/branches"
        tags_url = f"{repo_url}/tags"
        trunk_url = f"{repo_url}/trunk"

        branches = []

        # 列出branches目录
        stdout, stderr, code = self._run_command([self.svn_cmd, "ls", branches_url])
        if code == 0 and stdout:
            print("\n🌿 branches 分支:")
            print("-" * 60)
            for line in stdout.strip().split("\n"):
                if line.strip():
                    branches.append(f"branches/{line.strip()}")
                    # print(f"  • {line.strip()}")

        # 列出tags目录
        stdout, stderr, code = self._run_command([self.svn_cmd, "ls", tags_url])
        if code == 0 and stdout:
            print("\n🏷️ tags 标签:")
            print("-" * 60)
            for line in stdout.strip().split("\n"):
                if line.strip():
                    branches.append(f"tags/{line.strip()}")
                    print(f"  • {line.strip()}")

        # 检查trunk是否存在
        stdout, stderr, code = self._run_command([self.svn_cmd, "ls", trunk_url])
        if code == 0:
            branches.append("trunk")
            print("\n🌲 trunk (主干):")
            print("-" * 60)
            print("  • trunk")

        # 如果以上都失败，尝试列出根目录
        if not branches:
            stdout, stderr, code = self._run_command([self.svn_cmd, "ls", repo_url])
            if code == 0 and stdout:
                print("\n📁 仓库根目录结构:")
                print("-" * 60)
                for line in stdout.strip().split("\n"):
                    if line.strip():
                        branches.append(line.strip())
                        print(f"  • {line.strip()}")

        return branches

    def get_log(self, repo_url, limit=20):
        """
        获取提交日志

        :param repo_url: SVN仓库URL
        :param limit: 返回条数限制
        :return: 日志列表
        """
        # print(f"🔍 正在获取 {repo_url} 的提交日志...")

        cmd_args = [self.svn_cmd, "log", "-l", str(limit), "--xml", repo_url]
        stdout, stderr, code = self._run_command(cmd_args)

        if code != 0:
            print(f"❌ 获取日志失败: {stderr}")
            return []

        return self._parse_xml_log(stdout)

    def get_first_log(self, repo_url):
        """
        获取最初的提交记录

        :param repo_url: SVN仓库URL
        :return: 最初的提交记录
        """
        # print(f"🔍 正在获取 {repo_url} 的最初提交记录...")

        # 获取所有日志（从第1条开始，获取1条）
        cmd_args = [self.svn_cmd, "log", "-r", "1:1", "--xml", repo_url]
        stdout, stderr, code = self._run_command(cmd_args)

        if code != 0:
            # 尝试其他方式获取最早的提交
            cmd_args = [self.svn_cmd, "log", "-r", "HEAD:1", "--xml", repo_url]
            stdout, stderr, code = self._run_command(cmd_args)

        if code != 0:
            print(f"❌ 获取日志失败: {stderr}")
            return None

        logs = self._parse_xml_log(stdout)
        if logs:
            return logs[-1] if len(logs) > 1 else logs[0]

        return None

    def _parse_xml_log(self, xml_content):
        """
        解析SVN日志的XML输出

        :param xml_content: XML内容
        :return: 日志列表
        """
        logs = []

        # 使用正则解析XML（简单方式）
        entry_pattern = r"<logentry[^>]*>(.*?)</logentry>"
        entries = re.findall(entry_pattern, xml_content, re.DOTALL)

        for entry in entries:
            log = {}

            # 获取版本号
            rev_match = re.search(r"<revision>(\d+)</revision>", entry)
            if rev_match:
                log["revision"] = int(rev_match.group(1))

            # 获取作者
            author_match = re.search(r"<author>([^<]+)</author>", entry)
            if author_match:
                log["author"] = author_match.group(1)

            # 获取日期
            date_match = re.search(r"<date>([^<]+)</date>", entry)
            if date_match:
                log["date"] = date_match.group(1)

            # 获取注释
            msg_match = re.search(r"<msg>([^<]*)</msg>", entry)
            if msg_match:
                log["message"] = msg_match.group(1).strip()

            logs.append(log)

        return logs

    def checkout(self, repo_url, local_path):
        """
        拉取代码到本地

        :param repo_url: SVN仓库URL
        :param local_path: 本地路径
        :return: 是否成功
        """
        print(f"📥 正在拉取代码: {repo_url} -> {local_path}")

        cmd_args = [self.svn_cmd, "checkout", repo_url, local_path]
        stdout, stderr, code = self._run_command(cmd_args)

        if code == 0:
            print("✅ 拉取成功！")
            return True
        else:
            print(f"❌ 拉取失败: {stderr}")
            return False

    def show_log_details(self, logs):
        """
        显示日志详情

        :param logs: 日志列表
        """
        if not logs:
            print("❌ 没有获取到日志信息")
            return

        print("\n📋 提交日志:")
        print("=" * 80)

        for log in logs:
            print(f"\n版本: {log.get('revision', '未知')}")
            print(f"作者: {log.get('author', '未知')}")
            print(f"日期: {log.get('date', '未知')}")
            print(f"注释: {log.get('message', '无')}")
            print("-" * 60)

    def show_log_table(self, logs, branch="trunk"):
        """
        以表格形式显示日志详情

        :param logs: 日志列表
        :param branch: 分支名称
        """
        if not logs:
            print("❌ 没有获取到日志信息")
            return

        # 打印表头
        print("\n" + "=" * 60)
        print(f"{'分支':<30} {'提交人':<25}")
        print("-" * 60)

        # 打印每行数据
        for log in logs:
            print(f"{branch:<30} {log.get('author', '未知'):<25}")

        print("=" * 60)

    def get_all_branches_first_log(self, repo_url):
        """
        获取所有分支（包括主干）的最后一次提交记录

        :param repo_url: SVN仓库URL
        :return: 分支信息列表
        """
        # print(f"🔍 正在获取 {repo_url} 所有分支的最后提交记录...")

        # 获取分支列表
        branches = self.list_branches(repo_url)

        if not branches:
            print("❌ 未找到任何分支")
            return []

        # 存储所有分支的最后提交信息
        results = []

        # 遍历每个分支，获取最后一次提交
        for branch in branches:
            branch_url = (
                f"{repo_url}/{branch}"
                if not repo_url.endswith("/")
                else f"{repo_url}{branch}"
            )

            # print(f"\n⏳ 正在获取 {branch} 的最后提交...")
            # 获取最近1条日志（即最后一次提交）
            logs = self.get_log(branch_url, limit=1)

            if logs:
                last_log = logs[0]
                results.append(
                    {
                        "branch": branch,
                        "message": last_log.get("message", "无"),
                        "author": last_log.get("author", "未知"),
                        "revision": last_log.get("revision", "未知"),
                    }
                )
            else:
                results.append(
                    {
                        "branch": branch,
                        "message": "无法获取",
                        "author": "未知",
                        "revision": "未知",
                    }
                )

        return results

    def show_all_branches_first_log_table(self, repo_url):
        """
        获取所有分支的最后提交记录并以表格形式显示

        :param repo_url: SVN仓库URL
        """
        branch_logs = self.get_all_branches_first_log(repo_url)

        if not branch_logs:
            return

        # 打印表头
        print("\n" + "=" * 90)
        print(f"{'分支':<25} {'提交人':<15} {'日志':<45}")
        print("-" * 90)

        # 打印每行数据
        for item in branch_logs:
            message = item.get("message", "无")
            # 日志过长时截断
            if len(message) > 43:
                message = message[:43] + "..."
            print(f"{item['branch']:<25} {item['author']:<15} {message:<45}")

        print("=" * 90)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="SVN操作工具 - 获取分支、提交注释和人员信息",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 列出分支
  python svn_utils.py --list-branches https://svn.example.com/repo

  # 获取最近20条提交日志
  python svn_utils.py --log https://svn.example.com/repo

  # 以表格格式显示（分支 | 注释 | 提交人）
  python svn_utils.py --log https://svn.example.com/repo/branches/dev --table

  # 获取最初的提交记录
  python svn_utils.py --first-log https://svn.example.com/repo

  # 获取所有分支和主干的最初提交记录（表格格式）
  python svn_utils.py --all-first https://svn.example.com/repo

  # 拉取代码到本地
  python svn_utils.py --checkout https://svn.example.com/repo ./local_dir
        """,
    )

    parser.add_argument(
        "--list-branches", metavar="REPO_URL", help="列出SVN仓库的分支结构"
    )
    parser.add_argument("--log", metavar="REPO_URL", help="获取提交日志")
    parser.add_argument("--first-log", metavar="REPO_URL", help="获取最初的提交记录")
    parser.add_argument(
        "--checkout", nargs=2, metavar=("REPO_URL", "LOCAL_PATH"), help="拉取代码到本地"
    )
    parser.add_argument(
        "-l", "--limit", type=int, default=20, help="日志条数限制（默认20）"
    )
    parser.add_argument(
        "--table", action="store_true", help="以表格格式显示（分支 | 注释 | 提交人）"
    )
    parser.add_argument(
        "--all-first", metavar="REPO_URL", help="获取所有分支和主干的最初提交记录"
    )

    args = parser.parse_args()

    if not any(
        [args.list_branches, args.log, args.first_log, args.checkout, args.all_first]
    ):
        parser.print_help()
        sys.exit(1)

    svn = SVNUtils()

    if args.list_branches:
        svn.list_branches(args.list_branches)

    if args.log:
        logs = svn.get_log(args.log, args.limit)
        if args.table:
            # 获取分支名称
            branch = args.log.rstrip("/").split("/")[-1]
            svn.show_log_table(logs, branch)
        else:
            svn.show_log_details(logs)

    if args.all_first:
        svn.show_all_branches_first_log_table(args.all_first)

    if args.first_log:
        log = svn.get_first_log(args.first_log)
        if log:
            print("\n🎉 最初的提交记录:")
            print("=" * 60)
            print(f"版本: {log.get('revision', '未知')}")
            print(f"作者: {log.get('author', '未知')}")
            print(f"日期: {log.get('date', '未知')}")
            print(f"注释: {log.get('message', '无')}")

    if args.checkout:
        repo_url, local_path = args.checkout
        svn.checkout(repo_url, local_path)


if __name__ == "__main__":
    main()
    # 运行方式：python util/svn_utils.py --list-branches https://svn.example.com/repo
    # 或 python util/svn_utils.py --log https://svn.example.com/repo
