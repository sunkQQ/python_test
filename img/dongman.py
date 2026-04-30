import requests
from bs4 import BeautifulSoup
import os

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

url = "https://www.4k88.com/dongman/"
save_dir = "动漫壁纸"
os.makedirs(save_dir, exist_ok=True)

res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, "html.parser")
img_tags = soup.find_all("img")

count = 1
for img in img_tags:
    src = img.get("data-src") or img.get("src")
    if not src:
        continue
    if src.startswith("//"):
        src = "https:" + src
    if not src.startswith("http"):
        continue

    try:
        img_data = requests.get(src, headers=headers, timeout=10).content
        with open(f"{save_dir}/{count}.jpg", "wb") as f:
            f.write(img_data)
        count += 1
    except:
        continue

print(f"✅ 动漫图下载完成，共{count-1}张")
