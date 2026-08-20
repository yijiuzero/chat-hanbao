"""[hanbao modification] 处理用户提供的 hanbao.jpg 肖像，产出 3 张 png 用于 logo/favicon。
- hanbao-portrait-source.png: 源图归档（不嵌入）
- hanbao-portrait-logo.png:    高 240px，用于 logo-light/dark.svg 内嵌
- hanbao-portrait-favicon.png: 256x256 头肩特写，用于 favicon
"""
from PIL import Image
import os

SRC = r"C:\Users\wjh18\Pictures\hanbao.jpg"
PUB = r"F:\work\chat-hanbao\console\public"
os.makedirs(PUB, exist_ok=True)

img = Image.open(SRC)
print("source:", img.size, img.mode)
w, h = img.size

# 1) 源图归档（PNG, 白底转 RGB, optimize）
src_img = img.convert("RGB")
src_img.save(os.path.join(PUB, "hanbao-portrait-source.png"), "PNG", optimize=True)

# 2) logo 用图：保持比例, 高 240, PNG 优化
ratio = 240 / h
logo_w = int(w * ratio)
logo_img = img.resize((logo_w, 240), Image.LANCZOS).convert("RGB")
logo_img.save(os.path.join(PUB, "hanbao-portrait-logo.png"), "PNG", optimize=True)

# 3) favicon 用图：裁剪头肩特写（脸 + 一点点龙纹 start）→ 缩 256x256
# 源图人物脸在中上部(25%~55% y), 我们裁 y 10%~78%, x 中部裁掉边上
crop_box = (int(w * 0.10), int(h * 0.05), int(w * 0.90), int(h * 0.78))
fav_raw = img.crop(crop_box)
fav_img = fav_raw.resize((256, 256), Image.LANCZOS).convert("RGB")
fav_img.save(os.path.join(PUB, "hanbao-portrait-favicon.png"), "PNG", optimize=True)

for f in [
    "hanbao-portrait-source.png",
    "hanbao-portrait-logo.png",
    "hanbao-portrait-favicon.png",
]:
    p = os.path.join(PUB, f)
    print(f, os.path.getsize(p), "bytes")
