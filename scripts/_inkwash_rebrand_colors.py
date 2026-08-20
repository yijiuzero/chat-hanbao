# [hanbao modification] 阶段6 T6 水墨风：组件级硬编码色一次性换成水墨色系
# 批量替换脚本。务必用二进制读写，避免 LF<->CRLF 破坏换行符（曾致 git diff 爆量）。
import os
import re

ROOT = r"F:\work\chat-hanbao\console\src"
# App.tsx 已是水墨 token，且注释里提到旧橙 #FF8C42 作说明，跳过以免误改注释
SKIP_FILES = {"App.tsx"}

# 替换规则：(正则, 替换模版)。alpha 用捕获组保留。
RULES = [
    # 品牌橙 #FF8C42（T5 的 A 暖橘）→ 朱砂红（canvas/内联样式全安全，var 回退也变红）
    (re.compile(r"#FF8C42", re.IGNORECASE), "#C0392B"),
    # 上游 qwenpaw 旧橙的 rgba 形式 → 朱砂红 rgba
    (re.compile(r"rgba\(\s*255\s*,\s*127\s*,\s*22\s*,\s*([\d.]+)\s*\)"), r"rgba(192, 57, 43, \1)"),
    # 上游暖棕 hover/fill（rgba(43,18,0,*)）→ 墨色 rgba
    (re.compile(r"rgba\(\s*43\s*,\s*18\s*,\s*0\s*,\s*([\d.]+)\s*\)"), r"rgba(31, 31, 31, \1)"),
    # 亮底 qwenpaw 米灰 → 宣纸米白（带负向前瞻防部分匹配更长 hex）
    (re.compile(r"#f9f8f4(?![0-9a-fA-F])", re.IGNORECASE), "#F2EEE4"),
    (re.compile(r"#f9f7f3(?![0-9a-fA-F])", re.IGNORECASE), "#F2EEE4"),
    # 暗底浅黑 → 墨灰
    (re.compile(r"#1a1a1a(?![0-9a-fA-F])", re.IGNORECASE), "#161616"),
    # 深橙强调 #d45b0a → 朱砂红
    (re.compile(r"#d45b0a(?![0-9a-fA-F])", re.IGNORECASE), "#9E2B25"),
    # qwenpaw 蓝（链接/图表/焦点）：#1677ff 与 Tailwind 蓝 #3b82f6 → 石板灰（canvas 安全，与朱砂红组成水墨双色）
    (re.compile(r"#1677ff(?![0-9a-fA-F])", re.IGNORECASE), "#5C6B73"),
    (re.compile(r"#3b82f6(?![0-9a-fA-F])", re.IGNORECASE), "#5C6B73"),
]

EXTS = {".less", ".css", ".tsx", ".ts"}


def walk_files():
    for dirpath, _dirs, files in os.walk(ROOT):
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext in EXTS:
                yield os.path.join(dirpath, fn)


def main():
    total_files = 0
    total_subs = 0
    changed = []
    for path in walk_files():
        base = os.path.basename(path)
        if base in SKIP_FILES:
            continue
        with open(path, "rb") as f:
            data = f.read()
        text = data.decode("utf-8")
        new_text = text
        cnt = 0
        for rx, repl in RULES:
            new_text, n = rx.subn(repl, new_text)
            cnt += n
        if cnt > 0:
            with open(path, "wb") as f:
                f.write(new_text.encode("utf-8"))
            total_files += 1
            total_subs += cnt
            changed.append((os.path.relpath(path, ROOT), cnt))
    print(f"files changed: {total_files}, total substitutions: {total_subs}")
    for rel, c in sorted(changed):
        print(f"  {c:4d}  {rel}")


if __name__ == "__main__":
    main()
