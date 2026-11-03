#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""频率优先切分 LXGW WenKai GB Screen 为 webfont 子集。

策略：
  - 核心包(core)   ：按汉字使用频率取前 CORE_N 个最常用字，聚成 *单个* woff2。
                     普通页面只需下载这一份 + 拉丁，覆盖约 98% 日常文本。
  - 兜底频带       ：其余汉字按频率均分为 FALLBACK_CHUNKS 个频带(fallback_1..N)，
                     仅在页面出现对应生僻字时才按需下载，且只下命中的那几带。
  - 拉丁 / 符号    ：窄区间保持单文件。
浏览器依据各 @font-face 的 unicode-range 自动按需加载，常用字真正"聚在一起"。

调参（环境变量，或直接在下方改默认值）：
  CORE_N          核心包包含的最常用汉字数（默认 2500 = 现代汉语一级常用字）
  FALLBACK_CHUNKS 兜底频带数量（默认 17；总分片 = 3 固定 + 17 = 20）
"""
import array
import os
import subprocess
from fontTools.ttLib import TTFont

FONT_NAME = "LXGWWenKaiGBScreen.ttf"
FAMILY = "LXGW WenKai GB Screen"
CORE_N = int(os.environ.get("CORE_N", "2500"))
FALLBACK_CHUNKS = int(os.environ.get("FALLBACK_CHUNKS", "17"))
RANK_FILE = "assets/cn_rank.txt"
CSS_TPL = ".github/templates/font-css.tpl"
DIST = "dist"


def load_rank():
    cps = []
    with open(RANK_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cps.append(int(line))
    return cps


def compact(cps):
    """把无序码点列表压成最少连续区间 [(start,end), ...]"""
    cps = sorted(set(cps))
    if not cps:
        return []
    out = []
    start = prev = cps[0]
    for c in cps[1:]:
        if c == prev + 1:
            prev = c
        else:
            out.append((start, prev))
            start = prev = c
    out.append((start, prev))
    return out


def range_str_css(ranges):
    """CSS 的 unicode-range 使用，必须带 U+ 前缀（CSS 标准）"""
    return ",".join(
        f"U+{a:X}" if a == b else f"U+{a:X}-U+{b:X}" for a, b in ranges
    )


def range_str_pyft(ranges):
    """pyftsubset --unicodes 使用，纯十六进制（fontTools 最兼容格式，避开 U+ 前缀歧义）"""
    return ",".join(
        f"{a:X}" if a == b else f"{a:X}-{b:X}" for a, b in ranges
    )


def font_codepoints():
    return set(TTFont(FONT_NAME).getBestCmap().keys())


def emit(name, cps):
    ranges = compact(cps)
    rs_css = range_str_css(ranges)
    rs_pyft = range_str_pyft(ranges)
    out = os.path.join(DIST, f"{name}.woff2")
    print(f">> {name}: {len(cps)} 字 -> {out}")
    subprocess.run(
        ["pyftsubset", FONT_NAME, f"--unicodes={rs_pyft}",
         "--flavor=woff2", "--no-hinting", "--layout-features=*",
         f"--output-file={out}"],
        check=True,
    )
    tpl = open(CSS_TPL, encoding="utf-8").read()
    css = (tpl
           .replace("{{FAMILY}}", FAMILY)
           .replace("{{SAFE_NAME}}", name)
           .replace("{{RANGE}}", rs_css))
    with open(os.path.join(DIST, "index.css"), "a", encoding="utf-8") as fh:
        fh.write(css)


def main():
    rank = load_rank()
    avail = font_codepoints()
    os.makedirs(DIST, exist_ok=True)
    open(os.path.join(DIST, "index.css"), "w", encoding="utf-8").close()

    # 拉丁 / 符号：窄区间单文件（覆盖 ASCII、CJK 标点/全角/假名等）
    emit("latin", [c for c in avail if 0x0020 <= c <= 0x024F])
    emit("symbols", [c for c in avail if 0x2000 <= c <= 0x303F])

    # 常用汉字：按频率排序，取字体中确实存在的；未收录进频率表的多余字形放最后兜底
    ranked_present = [c for c in rank if 0x4E00 <= c <= 0x9FFF and c in avail]
    extra = sorted(c for c in avail if 0x4E00 <= c <= 0x9FFF and c not in set(rank))
    ordered = ranked_present + extra

    core = ordered[:CORE_N]
    rest = ordered[CORE_N:]
    emit("core", core)

    n = max(1, FALLBACK_CHUNKS)
    size = max(1, (len(rest) + n - 1) // n)
    for i in range(n):
        band = rest[i * size:(i + 1) * size]
        if band:
            emit(f"fallback_{i + 1}", band)

    woff2 = [f for f in os.listdir(DIST) if f.endswith(".woff2")]
    print(f"=== woff2 文件总数: {len(woff2)} ===")


if __name__ == "__main__":
    main()
