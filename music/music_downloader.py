#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音乐下载器 - 支持网易云音乐搜索和下载

功能说明：
- 搜索网易云音乐歌曲（支持歌名、歌手搜索）
- 获取歌曲播放链接并下载为MP3格式
- 支持命令行参数和交互式操作两种模式

使用方法：
1. 交互式模式：python music_downloader.py
2. 命令行模式：python music_downloader.py "关键词" "下载序号"

注意事项：
- 部分歌曲受版权保护，需要登录账号才能下载
- 建议搜索纯音乐、翻唱等免费歌曲
- 请尊重音乐版权，支持正版音乐

@author: sunk
@since: 2026-05-07
"""

import os
import re
import json
import requests
import sys
import random
import time


class MusicDownloader:
    """
    多平台音乐下载器类

    核心功能：
    - 封装HTTP请求，添加随机延迟避免被限制
    - 调用网易云音乐API搜索歌曲
    - 获取歌曲播放链接
    - 下载并保存为MP3文件

    支持平台：网易云音乐
    """

    def __init__(self):
        """初始化下载器"""
        # 请求头，模拟浏览器访问
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://music.163.com/",
            "Accept": "application/json",
        }
        # 下载目录
        self.download_dir = "downloads"
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def _request(self, url, params=None, method="GET", timeout=10):
        """
        封装HTTP请求方法

        :param url: 请求URL
        :param params: 请求参数（字典）
        :param method: 请求方法（GET/POST）
        :param timeout: 超时时间（秒）
        :return: 返回JSON数据或文本内容，失败返回None
        """
        try:
            # 添加随机延迟，避免请求过快被限制
            time.sleep(random.uniform(0.3, 0.8))

            if method == "GET":
                response = requests.get(
                    url, headers=self.headers, params=params, timeout=timeout
                )
            else:
                response = requests.post(
                    url, headers=self.headers, data=params, timeout=timeout
                )

            # 检查HTTP状态码
            response.raise_for_status()

            # 尝试解析JSON，失败则返回文本
            try:
                return response.json()
            except:
                return response.text

        except requests.exceptions.Timeout:
            print("请求超时")
            return None
        except Exception as e:
            print(f"请求失败: {e}")
            return None

    def search_netease(self, keyword, page=1, page_size=10):
        """
        搜索网易云音乐歌曲

        :param keyword: 搜索关键词（歌名或歌手名）
        :param page: 页码（默认第1页）
        :param page_size: 每页数量（默认10首）
        :return: 歌曲列表，每首歌包含id、歌名、歌手、专辑、时长、链接
        """
        # 网易云音乐搜索API
        url = "https://music.163.com/api/search/get/web"
        params = {
            "s": keyword,  # 搜索关键词
            "type": 1,  # 搜索类型：1=单曲
            "offset": (page - 1) * page_size,  # 偏移量
            "limit": page_size,  # 返回数量
            "csrf_token": "",  # CSRF令牌（空即可）
        }

        # 发送请求
        result = self._request(url, params, method="POST")
        if not isinstance(result, dict):
            return []

        # 提取歌曲列表
        songs = result.get("result", {}).get("songs", [])
        song_list = []

        # 遍历处理每首歌曲
        for song in songs:
            song_info = {
                "id": song.get("id"),
                "song_name": song.get("name") or "未知",
                "singer": "/".join(
                    [artist.get("name") for artist in song.get("artists", [])]
                ),
                "album": song.get("album", {}).get("name") or "未知",
                "duration": self._format_duration(song.get("duration", 0)),
                "url": f"https://music.163.com/song?id={song.get('id')}",
            }
            song_list.append(song_info)

        return song_list

    def _format_duration(self, duration):
        """
        格式化歌曲时长（毫秒转分:秒格式）

        :param duration: 时长（毫秒）
        :return: 格式化后的时长字符串（如 "04:30"）
        """
        minutes = duration // 60000
        seconds = (duration % 60000) // 1000
        return f"{minutes:02d}:{seconds:02d}"

    def get_netease_play_url(self, song_id):
        """
        获取网易云音乐歌曲播放URL

        :param song_id: 歌曲ID
        :return: 播放URL（成功）或None（失败）
        """
        # 获取播放链接API
        url = f"https://music.163.com/api/song/enhance/player/url"
        params = {
            "ids": f"[{song_id}]",  # 歌曲ID列表
            "br": 320000,  # 音质：320kbps（最高音质）
            "csrf_token": "",  # CSRF令牌
        }

        # 发送请求
        result = self._request(url, params, method="POST")
        if isinstance(result, dict):
            data = result.get("data", [])
            if data:
                play_url = data[0].get("url")
                if play_url:
                    return play_url

        return None

    def download_song(self, song_info):
        """
        下载歌曲并保存为MP3文件

        :param song_info: 歌曲信息字典（包含id、song_name、singer等）
        :return: True（下载成功）或False（下载失败）
        """
        song_id = song_info.get("id")
        song_name = song_info.get("song_name")
        singer = song_info.get("singer")

        # 检查歌曲ID是否存在
        if not song_id:
            print(f"❌ 无法获取歌曲ID: {song_name}")
            return False

        # 获取播放链接
        print(f"\n🔍 正在获取 {song_name} - {singer} 的下载链接...")
        play_url = self.get_netease_play_url(song_id)

        # 检查播放链接是否获取成功
        if not play_url:
            print(f"❌ 无法获取播放链接: {song_name}")
            print("💡 提示：部分歌曲受版权保护，需要登录账号才能下载")
            print(f"🌐 您可以访问网页试听: {song_info.get('url')}")
            print("📱 建议在网易云音乐客户端中登录账号后下载")
            print("\n⚠️ 版权声明：请尊重音乐版权，支持正版音乐")
            return False

        # 开始下载
        print(f"✅ 获取到播放链接")
        print(f"📥 正在下载 {song_name} - {singer}...")

        try:
            # 流式下载（适合大文件）
            response = requests.get(
                play_url, headers=self.headers, stream=True, timeout=30
            )
            response.raise_for_status()

            # 验证内容类型是否为音频
            content_type = response.headers.get("content-type", "")
            if "audio" not in content_type and "octet-stream" not in content_type:
                print("❌ 下载失败：获取的不是音频文件")
                print("💡 可能该歌曲需要登录才能下载")
                return False

            # 生成文件名并清理非法字符
            filename = f"{song_name} - {singer}.mp3"
            filename = self._clean_filename(filename)
            filepath = os.path.join(self.download_dir, filename)

            # 获取文件大小
            total_size = int(response.headers.get("content-length", 0))
            downloaded_size = 0

            # 写入文件并显示进度
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        # 显示下载进度
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(
                                f"\r进度: [{('=' * int(progress//5)).ljust(20)}] {progress:.1f}%",
                                end="",
                            )

            print(f"\n🎉 下载完成！文件保存到: {filepath}")
            return True

        except requests.exceptions.Timeout:
            print("❌ 下载超时")
            return False
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            print("💡 提示：部分歌曲受版权保护，需要登录账号才能下载")
            return False

    def _clean_filename(self, filename):
        """
        清理文件名中的非法字符

        :param filename: 原始文件名
        :return: 清理后的文件名
        """
        invalid_chars = r'[\\/:*?"<>|]'
        return re.sub(invalid_chars, "_", filename)


def main():
    """主函数：处理用户输入并执行下载流程"""
    # 打印欢迎信息
    print("=" * 50)
    print("🎵 多平台音乐下载器")
    print("=" * 50)
    print("支持平台：网易云音乐")
    print("=" * 50)
    print("⚠️ 注意：受版权保护的歌曲需要登录账号才能下载")
    print("💡 建议：可以尝试搜索一些翻唱、纯音乐或免费歌曲")
    print()

    # 创建下载器实例
    downloader = MusicDownloader()

    # 获取搜索关键词（支持命令行参数或交互式输入）
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
    else:
        keyword = input("请输入歌名或歌手名: ")

    # 验证关键词
    if not keyword.strip():
        print("❌ 关键词不能为空")
        return

    # 搜索歌曲
    print(f"🔍 正在搜索: {keyword}")
    songs = downloader.search_netease(keyword)

    # 检查搜索结果
    if not songs:
        print("❌ 未找到相关歌曲")
        return

    # 显示搜索结果
    print(f"\n搜索结果 ({len(songs)} 首):")
    print("-" * 60)
    for i, song in enumerate(songs, 1):
        print(f" {i}. {song['song_name']}")
        print(f"    歌手: {song['singer']}")
        print(f"    专辑: {song['album']}")
        print(f"    时长: {song['duration']}")
        print(f"    链接: {song['url']}")

    # 获取用户选择（支持命令行参数或交互式输入）
    if len(sys.argv) > 2:
        choice = sys.argv[2]
    else:
        print("\n请选择要下载的歌曲序号（多个用逗号分隔，如 1,3,5）: ")
        choice = input("输入序号: ")

    # 验证选择
    if not choice.strip():
        print("❌ 请输入有效的序号")
        return

    # 解析选择的序号
    try:
        indices = [int(x.strip()) - 1 for x in choice.split(",") if x.strip()]
    except ValueError:
        print("❌ 请输入有效的数字序号")
        return

    # 下载选中的歌曲
    for idx in indices:
        if 0 <= idx < len(songs):
            downloader.download_song(songs[idx])
        else:
            print(f"❌ 无效的序号: {idx + 1}")

    # 结束提示
    print("\n" + "=" * 50)
    print("操作完成")
    print("=" * 50)


if __name__ == "__main__":
    # 程序入口
    main()
