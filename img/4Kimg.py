import requests
from bs4 import BeautifulSoup
import os

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.4k88.com/",
}

url = "https://www.4k88.com/fengjing/"
save_dir = "4K风景壁纸"
os.makedirs(save_dir, exist_ok=True)

res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, "html.parser")
img_tags = soup.find_all("img")

count = 1
for img in img_tags:
    # 兼容：data-src / src 两种
    src = img.get("data-src") or img.get("src")
    if not src:
        continue
    if src.startswith("//"):
        src = "https:" + src
    if not src.startswith("http"):
        continue

    try:
        print(f"下载第{count}张：{src}")
        img_data = requests.get(src, headers=headers, timeout=10).content
        with open(f"{save_dir}/{count}.jpg", "wb") as f:
            f.write(img_data)
        count += 1
    except Exception as e:
        print("失败跳过")

print(f"\n✅ 完成，共下载 {count-1} 张")
