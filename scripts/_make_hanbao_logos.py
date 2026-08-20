"""[hanbao modification] 生成 logo-light.svg / logo-dark.svg / hanbao-icon.svg,
内嵌 hanbao-portrait-{logo,favicon}.png 的 base64, 替换旧函包图标.
"""
import base64
import os

PUB = r"F:\work\chat-hanbao\console\public"


def b64png(name: str) -> str:
    with open(os.path.join(PUB, name), "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


logo_b64 = b64png("hanbao-portrait-logo.png")
fav_b64 = b64png("hanbao-portrait-favicon.png")

# --- logo-light.svg (亮色主题: 白底水墨肖像 + 深色 wordmark) ---
logo_light = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 320 60" width="320" height="60">
  <!-- [hanbao modification] hanbao 品牌 logo：墨韵古典肖像 + wordmark, 适配亮色主题 -->
  <defs>
    <linearGradient id="cornerOrnament" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#1f1f1f" stop-opacity="0"/>
      <stop offset="100%" stop-color="#1f1f1f" stop-opacity="0.18"/>
    </linearGradient>
  </defs>
  <!-- portrait: 1024x1024 缩到 52x52, 白色卡片背, 让图自带白底在亮主题上自然 -->
  <rect x="3" y="3" width="54" height="54" rx="8" fill="#FFFFFF" stroke="#E8E8E8" stroke-width="0.5"/>
  <image href="data:image/png;base64,{logo_b64}" x="3" y="3" width="54" height="54" preserveAspectRatio="xMidYMid slice"/>
  <rect x="3" y="3" width="54" height="54" rx="8" fill="url(#cornerOrnament)" pointer-events="none"/>
  <!-- wordmark「hanbao」: 深色, 带微弱字距, 站点名 -->
  <text x="70" y="40" font-family="'Songti SC','Noto Serif SC','Source Han Serif SC',STSong,serif" font-size="30" font-weight="700" fill="#1f1f1f" letter-spacing="1.5">hanbao</text>
</svg>'''

# --- logo-dark.svg (暗色主题: 白底水墨肖像 + 浅色 wordmark) ---
logo_dark = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 320 60" width="320" height="60">
  <!-- [hanbao modification] hanbao 品牌 logo：墨韵古典肖像 + wordmark, 适配暗色主题 -->
  <defs>
    <linearGradient id="cornerOrnament" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0.12"/>
    </linearGradient>
  </defs>
  <rect x="3" y="3" width="54" height="54" rx="8" fill="#FFFFFF" stroke="#FFFFFF" stroke-width="0.5"/>
  <image href="data:image/png;base64,{logo_b64}" x="3" y="3" width="54" height="54" preserveAspectRatio="xMidYMid slice"/>
  <rect x="3" y="3" width="54" height="54" rx="8" fill="url(#cornerOrnament)" pointer-events="none"/>
  <text x="70" y="40" font-family="'Songti SC','Noto Serif SC','Source Han Serif SC',STSong,serif" font-size="30" font-weight="700" fill="#f5f5f5" letter-spacing="1.5">hanbao</text>
</svg>'''

# --- hanbao-icon.svg (favicon: 方形头像特写, 全画幅) ---
favicon = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 64 64" width="64" height="64">
  <!-- [hanbao modification] hanbao favicon：水墨肖像头肩特写, 白底, 边框圆角 -->
  <defs>
    <clipPath id="iconClip">
      <rect x="0" y="0" width="64" height="64" rx="12"/>
    </clipPath>
  </defs>
  <g clip-path="url(#iconClip)">
    <rect x="0" y="0" width="64" height="64" fill="#FFFFFF"/>
    <image href="data:image/png;base64,{fav_b64}" x="0" y="0" width="64" height="64" preserveAspectRatio="xMidYMid slice"/>
  </g>
  <rect x="0.5" y="0.5" width="63" height="63" rx="11.5" fill="none" stroke="#E8E8E8" stroke-width="1"/>
</svg>'''

with open(os.path.join(PUB, "logo-light.svg"), "w", encoding="utf-8", newline="") as f:
    f.write(logo_light)
with open(os.path.join(PUB, "logo-dark.svg"), "w", encoding="utf-8", newline="") as f:
    f.write(logo_dark)
with open(os.path.join(PUB, "hanbao-icon.svg"), "w", encoding="utf-8", newline="") as f:
    f.write(favicon)

for f in ["logo-light.svg", "logo-dark.svg", "hanbao-icon.svg"]:
    p = os.path.join(PUB, f)
    print(f, os.path.getsize(p), "bytes")
