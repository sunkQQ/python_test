import requests
from bs4 import BeautifulSoup
import os

headers = {"User-Agent": "Mozilla/5.0"}

# 改成你想爬的网址
url = "这里换成你要的网址"
save_dir = "通用图片"
os.makedirs(save_dir, exist_ok=True)

res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, "html.parser")
img_tags = soup.find_all("img")

count = 1
for img in img_tags:
    src = img.get("data-src") or img.get("data-original") or img.get("src")
    if not src:
        continue
    if src.startswith("//"):
        src = "https:" + src
    if not src.startswith("http"):
        continue
    try:
        data = requests.get(src, headers=headers, timeout=8).content
        with open(f"{save_dir}/{count}.jpg", "wb") as f:
            f.write(data)
        count += 1
    except:
        pass

print("✅ 全部爬取结束")
