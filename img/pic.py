import requests
import os

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome 120.0.0.0 Safari/537.36"
}

# 稳定免费壁纸网站，绝对能爬
url = "https://image.baidu.com/search/detail?adpicid=0&b_applid=11885264925017554091&bdtype=0&commodity=&copyright=&cs=1239282310%2C1704597852&di=7625305553161420801&fr=click-pic&fromurl=http%253A%252F%252Fwww.douyin.com%252Fnote%252F7510561059944025407&gsm=1e&hd=&height=0&hot=&ic=&ie=utf-8&imgformat=&imgratio=&imgspn=0&is=3549185769%2C3098786995&isImgSet=&latest=&lid=&lm=&objurl=https%253A%252F%252Fp3-pc-sign.douyinpic.com%252Ftos-cn-i-0813%252FoQvoPD9AAxBO36xip3ieeEA3AOAmIgCytNACWA~tplv-dy-aweme-images%253Aq75.webp&os=3549185769%2C3098786995&pd=image_content&pi=0&pn=3&rn=1&simid=1239282310%2C1704597852&tn=baiduimagedetail&width=0&word=%E5%87%A1%E4%BA%BA%E4%BC%91%E9%97%B2%E4%BC%A0%E7%B4%AB%E7%81%B5&z="

os.makedirs("美女壁纸", exist_ok=True)

res = requests.get(url, headers=headers)
html = res.text

# 匹配所有高清图片链接
import re

img_urls = re.findall(r"https://.*?\.jpg", html)

num = 1
for img in img_urls:
    try:
        print(f"正在下载第{num}张")
        pic = requests.get(img, headers=headers).content
        with open(f"美女壁纸/{num}.jpg", "wb") as f:
            f.write(pic)
        num += 1
    except:
        continue

print("下载完毕！去文件夹查看")
