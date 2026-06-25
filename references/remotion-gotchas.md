# Remotion 趟平的坑（这套技能的核心价值，逐条带病因+解法）

## 🔴 1. 浏览器：别下载、别用系统 Chrome —— 用干净的 chrome-headless-shell
**症状**：① 首次 `remotion render` 卡很久无输出（在偷偷下 93MB 浏览器，过代理常"20秒无数据"反复重试，几乎下不动）；② 改用系统 Chrome（`--browser-executable=".../Google Chrome"`）后报 `Visited "http://localhost:3001/index.html" but got no response`。

**病因**：① Remotion 首渲要拉 chrome-headless-shell，网络/代理差时极慢；② **系统 Chrome 带用户配置/可能已开着，Remotion 控不住它**（不是代理问题——本机代理 bypass 里通常已有 localhost）。

**解法**：用一份**干净的 `chrome-headless-shell`** 经 `--browser-executable` 指过去。本机大概率已有(playwright 装的)：
```bash
# macOS:
ls ~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell
# Linux:
ls ~/.cache/ms-playwright/chromium_headless_shell-*/chrome-linux*/chrome-headless-shell
# 选最新的一个：
npx remotion render <CompId> out.mp4 --browser-executable="<上面的路径>"
```
> `scripts/render.sh` 已把 macOS + Linux 两套缓存路径都查了,直接用它最省事。
没有就让 Remotion 下一次(`npx remotion browser ensure`，过代理慢但只需一次)。`scripts/render.sh` 已封装"自动找干净浏览器"。

> 排查口诀：`localhost:3001 no response` ≠ 代理 → 99% 是"浏览器不干净/控不住",换 headless-shell。

## 🔴 2. 确定性（渲染逐帧 seek，必须每帧可复现）
- 动画一律由 `interpolate(useCurrentFrame(), [f0,f1], [v0,v1], {easing:Easing.out(Easing.cubic), extrapolateLeft/Right:'clamp'})` 或 `spring()` 驱动。
- **禁** `Math.random()`、`Date.now()`、`new Date()`、计时器。
- **rough.js 必须传固定 `seed`**（如 `seed: 7 + index`），否则手绘抖动每帧都变。canvas 在 `useEffect` 里按尺寸画一次即可。

## 🔴 3. 装依赖按锁文件用对包管理器
看根目录锁文件：`package-lock.json`→`npm`，`pnpm-lock.yaml`→`pnpm`，`yarn.lock`→`yarn`，`bun.lockb`→`bun`。create-video 默认出 `package-lock.json` → 全程 **npm**（混用会生第二个锁文件、依赖树打架）。

## 4. Tesseract OCR（定位文字框）—— 三个真实会栽的点
- 命令：`tesseract <图> stdout tsv`（默认 psm=3 做版面分析，**多栏/标题+正文混排读得准**）。
- ⚠️ **`conf` 是浮点字符串**（Tesseract 5.x 输出如 `96.0`）。用 `int(d["conf"])` 解析会抛 `ValueError` → 若被 except 吞掉就**逐词跳过 → 0 命中**（脚本里曾踩，已修为 `float`）。这是"OCR 跑了但 highlights 全空"的头号元凶。
- ⚠️ **同一词组在标题+正文各出现一次**：朴素"取首个匹配"会命中**标题**（页面靠上），多半不是你要高亮的正文。`ocr-to-highlights.py` 默认取**最靠下**的那个（`--occurrence last`≈正文），并在 >1 命中时 WARN 列出所有 y;要别的用 `--occurrence first|N`。
- ⚠️ **别无脑加 `--psm 6`**（假设单块,多区文章会把行/词序读乱 → 词组匹配失败）。本范例就栽过:psm6 匹配不到,默认 psm 一次就中。
- ⚠️ **0 命中要报错**：脚本在任一词组没放上时 `exit 1`,别静默 exit 0——否则批量管线会渲出"高亮全没"的废片还以为成功。
- TSV 列：`… left top width height conf text`。找词组 = 在**同一行**(block/par/line 相同)找连续的词,框取并集(min left/top, max right/bottom)。`scripts/ocr-to-highlights.py` 已实现。
- 装：`brew install tesseract`（带 eng）。brew 卡在 auto-update 时加 `HOMEBREW_NO_AUTO_UPDATE=1`;bottle 走 ghcr.io 慢就挂代理。

## 5. 高亮"在文字后面"（白底图上的标准技巧）
图是单张 PNG（文字烤进像素里，没法真放到文字后）。用 **`mixBlendMode:'multiply'`**：高亮画在图**上面**,但 multiply 让"白底×黄=黄、深字×黄≈深字" → 视觉上**像在文字后**。配 OCR 框定位、外层 `overflow:hidden` + `width` 从 0 渐开做左→右扫入。

## 6. 本地素材
- 图：`staticFile('x.png')`(放 `public/`) + `<Img>`。**不像 HyperFrames 要 base64**,Remotion 原生吃本地文件。
- 视频：`<OffthreadVideo>`(帧精准、离屏解码,比 `<Video>` 适合渲染)。
- 体积大的素材别进 git(`out/`、大 mp4 加 `.gitignore`)。

## 7. 代理（仅当合成要联网素材时才相关）
本机系统代理可能拦外网;但 `staticFile` 是本地、不过网。Remotion 自己装包/下浏览器走 npm/ghcr——慢就 `export all_proxy=http://127.0.0.1:12000 https_proxy=… http_proxy=…`。渲染本身（素材全本地时）不需要代理。
