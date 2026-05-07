#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import requests
import sys
import random
import time


class MusicDownloader:
    """
    多平台音乐下载器
    支持：网易云音乐、QQ音乐
    """

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://music.163.com/",
            "Accept": "application/json",
        }
        self.download_dir = "downloads"
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def _request(self, url, params=None, method="GET", timeout=10):
        """发送请求"""
        try:
            time.sleep(random.uniform(0.3, 0.8))
            if method == "GET":
                response = requests.get(
                    url, headers=self.headers, params=params, timeout=timeout
                )
            else:
                response = requests.post(
                    url, headers=self.headers, data=params, timeout=timeout
                )

            response.raise_for_status()

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
        搜索网易云音乐

        :param keyword: 关键词（歌名或歌手）
        :param page: 页码
        :param page_size: 每页数量
        :return: 歌曲列表
        """
        url = "https://music.163.com/api/search/get/web"
        params = {
            "s": keyword,
            "type": 1,  # 单曲
            "offset": (page - 1) * page_size,
            "limit": page_size,
            "csrf_token": "",
        }

        result = self._request(url, params, method="POST")
        if not isinstance(result, dict):
            return []

        songs = result.get("result", {}).get("songs", [])
        song_list = []

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
        """格式化时长"""
        minutes = duration // 60000
        seconds = (duration % 60000) // 1000
        return f"{minutes:02d}:{seconds:02d}"

    def get_netease_play_url(self, song_id):
        """
        获取网易云音乐播放URL

        :param song_id: 歌曲ID
        :return: 播放URL
        """
        url = f"https://music.163.com/api/song/enhance/player/url"
        params = {
            "ids": f"[{song_id}]",
            "br": 320000,  # 320kbps
            "csrf_token": "",
        }

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
        下载歌曲

        :param song_info: 歌曲信息字典
        :return: 下载是否成功
        """
        song_id = song_info.get("id")
        song_name = song_info.get("song_name")
        singer = song_info.get("singer")

        if not song_id:
            print(f"❌ 无法获取歌曲ID: {song_name}")
            return False

        print(f"\n🔍 正在获取 {song_name} - {singer} 的下载链接...")
        play_url = self.get_netease_play_url(song_id)

        if not play_url:
            print(f"❌ 无法获取播放链接: {song_name}")
            print("💡 提示：部分歌曲受版权保护，需要登录账号才能下载")
            print(f"🌐 您可以访问网页试听: {song_info.get('url')}")
            print("📱 建议在网易云音乐客户端中登录账号后下载")
            print("\n⚠️ 版权声明：请尊重音乐版权，支持正版音乐")
            return False

        print(f"✅ 获取到播放链接")
        print(f"📥 正在下载 {song_name} - {singer}...")

        try:
            response = requests.get(
                play_url, headers=self.headers, stream=True, timeout=30
            )
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "audio" not in content_type and "octet-stream" not in content_type:
                print("❌ 下载失败：获取的不是音频文件")
                print("💡 可能该歌曲需要登录才能下载")
                return False

            filename = f"{song_name} - {singer}.mp3"
            filename = self._clean_filename(filename)
            filepath = os.path.join(self.download_dir, filename)

            total_size = int(response.headers.get("content-length", 0))
            downloaded_size = 0

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
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
        """清理文件名中的非法字符"""
        invalid_chars = r'[\\/:*?"<>|]'
        return re.sub(invalid_chars, "_", filename)


def main():
    print("=" * 50)
    print("🎵 多平台音乐下载器")
    print("=" * 50)
    print("支持平台：网易云音乐")
    print("=" * 50)
    print("⚠️ 注意：受版权保护的歌曲需要登录账号才能下载")
    print("💡 建议：可以尝试搜索一些翻唱、纯音乐或免费歌曲")
    print()

    downloader = MusicDownloader()

    # 获取搜索关键词
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
    else:
        keyword = input("请输入歌名或歌手名: ")

    if not keyword.strip():
        print("❌ 关键词不能为空")
        return

    print(f"🔍 正在搜索: {keyword}")
    songs = downloader.search_netease(keyword)

    if not songs:
        print("❌ 未找到相关歌曲")
        return

    print(f"\n搜索结果 ({len(songs)} 首):")
    print("-" * 60)
    for i, song in enumerate(songs, 1):
        print(f" {i}. {song['song_name']}")
        print(f"    歌手: {song['singer']}")
        print(f"    专辑: {song['album']}")
        print(f"    时长: {song['duration']}")
        print(f"    链接: {song['url']}")

    # 获取用户选择
    if len(sys.argv) > 2:
        # 命令行参数模式
        choice = sys.argv[2]
    else:
        print("\n请选择要下载的歌曲序号（多个用逗号分隔，如 1,3,5）: ")
        choice = input("输入序号: ")

    if not choice.strip():
        print("❌ 请输入有效的序号")
        return

    # 解析选择
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

    print("\n" + "=" * 50)
    print("操作完成")
    print("=" * 50)


if __name__ == "__main__":
    main()
