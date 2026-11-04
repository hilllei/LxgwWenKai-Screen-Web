# LXGW WenKai GB Screen Webfont Builder
基于 **LXGW WenKai GB Screen（霞鹜文楷屏幕版）** 构建按需懒加载 WebFont。

按**汉字使用频率**切分，而非简单按码位区间均匀切：
- **核心包 `core`**：取使用频率最高的前 2500 个汉字（≈现代汉语一级常用字），聚成**单个** woff2。普通页面只需下载这一份 + 拉丁子集，即可覆盖约 98% 的日常中文。
- **兜底频带 `fallback_1..N`**：其余汉字按频率均分为 N 个频带，仅在页面出现对应生僻字时才按需下载，且只下命中的那几带。
- **拉丁 / 符号**：窄区间保持单文件。

浏览器依据各 `@font-face` 的 `unicode-range` 自动按需加载——**高频常用字真正聚在一起**，且文件数远少于"均匀切 84 片"的方案。

> 字频依据：`assets/cn_rank.txt`（取自 `cn-font-split` 的简体汉字使用频率排序表，已随仓库提交，构建时本地读取，不依赖网络）。

## ✨ 特性
- ✅ **频率优先切分**：常用字聚在核心包，生僻字延迟到兜底频带
- ✅ 产物约 **20 个 woff2**（拉丁 / 符号 / 核心 / 17 个兜底频带）+ `index.css`，文件数合理、单片更小
- ✅ 原生 `font-display: swap`：字体加载期间展示兜底字体，不会文字空白
- ✅ `--no-hinting` + woff2（brotli）压缩，屏幕显示无影响且体积更小
- ✅ GitHub Actions 手动构建，自动部署 GitHub Pages 并发布 Release
- ✅ 字体许可证： **SIL Open Font License 1.1**，免费商用

## 🔧 调参
编辑 `.github/workflows/build-font.yml` 里 `python build.py` 这一步，或直接在 `build.py` 顶部改默认值：
- `CORE_N`（默认 `2500`）：核心包包含的最常用汉字数。调小 → 核心包更小更快，但更多字落到兜底频带；调大 → 覆盖更全，核心包更大。
- `FALLBACK_CHUNKS`（默认 `17`）：兜底频带数量，越大单带越小、按需越精准，文件数也越多。总分片数 = 3（固定：拉丁 / 符号 / 核心）+ `FALLBACK_CHUNKS`。

> 例：把核心包压到约 1000 字，可设 `CORE_N=1000`；想更少文件（总分片约 13），可设 `FALLBACK_CHUNKS=10`；想更接近 20，保持默认 `17` 即可。

## 📦 产物结构
| 文件 | 内容 |
|---|---|
| `latin.woff2` | 英文、数字、基础 ASCII 标点 |
| `symbols.woff2` | CJK 全角符号、标点、假名等 |
| `core.woff2` | **前 2500 最常用汉字（核心包）** |
| `fallback_1.woff2` … `fallback_17.woff2` | 其余汉字按频率分的 17 个兜底频带 |

## 🍄 分片查看
`https://github.com/hilllei/LxgwWenKai-Screen-Web/tree/gh-pages`

## 📌 使用方式
引入产物 `index.css` 即可，`font-family` 为 **`LXGW WenKai GB Screen`**：

```html
<!-- 方式一：GitHub Pages 原生（Fastly 全球 CDN） -->
<link rel="stylesheet" href="https://hilllei.github.io/LxgwWenKai-Screen-Web/index.css">

<!-- 方式二：jsDelivr -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/hilllei/LxgwWenKai-Screen-Web@gh-pages/index.css">

<!-- 方式三：jsdmirror -->
<link rel="stylesheet" href="https://cdn.jsdmirror.com/gh/hilllei/LxgwWenKai-Screen-Web@gh-pages/index.css">

<style>
body {
  font-family: "LXGW WenKai GB Screen";
}
</style>
```

> 也可锁定到某次提交以获得不可变引用：
> `https://cdn.jsdelivr.net/gh/hilllei/LxgwWenKai-Screen-Web@<commit哈希>/index.css`


## 📜 许可证
- 字体：**SIL Open Font License 1.1**（免费商用）
- 构建脚本 / 字频表：与仓库许可证一致
