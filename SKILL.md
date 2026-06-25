---
name: vibemotion-remotion
description: 用 Remotion(React 视频框架)做"以素材为主"的视频——导入大量本地图片/视频做包装、给图片/截图加 OCR 定位的高亮/标注、参数化/批量出片。是 vibemotion-hyperframes(HyperFrames 纯代码图形)的姊妹技能:素材越重、越要批量/参数化,越用这个;纯代码动效图形用 vibemotion-hyperframes。已含一条验证过的范例(文章图 OCR 高亮 + 模糊渐清 + 微缩放/旋转)。
---

# vibemotion-remotion · Remotion 视频套件（素材 + OCR 高亮 + 批量）

Remotion = React 写视频(`useCurrentFrame()` 驱动每帧),自带成熟的**本地素材/视频管线**。这套技能封装"**以真实素材为主**"的视频活,补 vibemotion-hyperframes(HF)不擅长的场景。

> **⚠️ 用法哲学(先读,同 vibemotion-hyperframes)**：本技能是「**方法 + 验证过的范例 + 趟平的坑**」,**不是固定清单**。每次可以不一样——缺啥去 `references/`、`examples/`、`remotion-best-practices` 技能、Remotion 官方文档里找;要新效果照规范生成新的。守住「确定性(interpolate(frame)+固定 seed) + 用对干净浏览器」两条底线即可。

## 什么时候用这个 / 什么时候用 vibemotion-hyperframes(HF)
| 你要做的 | 用 |
|---|---|
| **一堆本地图片/视频做包装**(片头/字幕/转场叠在实拍/录屏上) | **本技能(Remotion)**——原生 `staticFile()` 吃本地素材 |
| **给图片/截图加 OCR 定位的高亮、圈注、标记** | **本技能**(见范例 `article-highlight`) |
| **参数化 / 批量**(同模板换数据出几十上百条) | **本技能**(Zod schema + `--props`) |
| 纯代码图形 MG(标题/数据/连线/形状,少量素材) | **vibemotion-hyperframes(HF)**——AI 写起来更顺 |
| 想让 AI 一句话快速出图形片 | **vibemotion-hyperframes(HF)** |

> 通用 Remotion 知识(动画/字幕/音频/图表/3D…)走已装的 **`remotion-best-practices`** 技能;本技能只加"素材+OCR+批量"的具体配方和趟平的坑。

## 能做哪些 Remotion 片(配方菜单 —— 选一个,或让我照规范生成新的)
这是个**会长大的菜单**:Remotion 能做的片很多,本技能每**验证**一种就收进 `examples/` 当可跑模板,供你挑。想要没列的,照用法哲学**新生成**(验证过再进菜单)。

| 配方 | 干啥 | 状态 |
|---|---|---|
| **article-highlight** | 图/截图 + OCR 定位高亮·圈注 + 模糊渐清 + 微缩放/3D旋转 | ✅ 已验证(`examples/article-highlight/`) |
| footage / 录屏包装 | 实拍/录屏打底 + 片头/字幕/转场/调色叠上去 | ⏳ 可做(`<OffthreadVideo>`) |
| 数据驱动 | 动态图表 / 数字滚动 / 排行榜(Zod 喂数据) | ⏳ 可做 |
| 批量 / 参数化 | 同模板 × N 份数据 → 几十上百条 | ⏳ 可做(`--props`) |
| 图集 Ken Burns | 一堆照片缓推拉 + 转场成片 | ⏳ 可做 |
| 字幕烧录 | 给视频烧 SRT / 逐字高亮字幕 | ⏳ 可做(`@remotion/captions`) |

> 用法:你报一种(或描述想要的),我照配方/规范做;新类型**验证过就进菜单当模板**,菜单越用越全。
> ⚠️ **`⏳` = Remotion 能做、但本技能还没真做透验证过的方向**(不是承诺);真要做时照规范现做 + 渲染验证,过了再标 ✅。**只有 ✅ 的才有可跑模板。**

## 做一条的流程
1. **建工程**(无则)：`npx create-video@latest --yes --blank --no-tailwind <名>`;装依赖**按锁文件用对包管理器**(有 `package-lock.json` → `npm i`)。
2. **放素材** → `public/`(图用 `staticFile('x.png')` + `<Img>`;视频 `<OffthreadVideo>`)。
3. **要 OCR 定位** → 跑 `scripts/ocr-to-highlights.py <图> "词1" "词2"` 出 `highlights.json`(Tesseract → 词框,原图 px)。
4. **写合成** → 照 `examples/article-highlight/` 改:`interpolate(frame,…,{easing:Easing…})` 做缩放/旋转/模糊,rough.js 高亮 `mixBlendMode:multiply`(白底图上=在文字后)。
5. 🔴 **渲染(必读 `references/remotion-gotchas.md`)**：
   ```bash
   bash scripts/render.sh <CompId> out.mp4    # 自动找干净 headless-shell,绕开下载/系统Chrome两大坑
   # 等价:npx remotion render <CompId> out.mp4 --browser-executable="<干净 chrome-headless-shell 路径>"
   ```

## 🚫 两条最容易栽的坑(详见 references/remotion-gotchas.md)
- 🚫 **别让 Remotion 自动下浏览器**(93MB,过代理常卡死),🚫 **也别用系统 Chrome**(带用户配置 → `localhost:3001 no response`)。✅ **用干净的 `chrome-headless-shell`**(playwright 缓存里就有:`~/Library/Caches/ms-playwright/chromium_headless_shell-*/.../chrome-headless-shell`)经 `--browser-executable` 指过去。`render.sh` 已自动处理。
- 🚫 渲染里别用 `Math.random()`/`Date.now()`;rough.js 必须给**固定 `seed`**,否则每帧抖。动画一律 `interpolate(useCurrentFrame(),…)`。

## 资源
- `references/recipe-article-highlight.md` —— ⭐这条范例的逐步配方(OCR→高亮在文字后→模糊渐清→微缩放/旋转)。
- `references/remotion-gotchas.md` —— ⭐趟平的坑(浏览器/代理localhost/npm锁文件/Tesseract psm/确定性)。
- `examples/article-highlight/` —— 验证过的真工程(`ArticleHighlight.tsx` + `Root.tsx` + `highlights.json` + 样例图),照它改。
- `scripts/ocr-to-highlights.py` —— 任意图跑 Tesseract → `highlights.json`(参数化)。
- `scripts/render.sh` —— 自动找干净浏览器并渲染。
- 姊妹技能 **vibemotion-hyperframes**(HyperFrames 纯代码图形)、**remotion-best-practices**(通用 Remotion)。
