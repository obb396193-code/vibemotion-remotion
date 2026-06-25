# article-highlight —— 验证过的 Remotion 范例

文章图 OCR 高亮:白底FHD居中文章 → 模糊渐清(0–1s)→ 5s 微缩放 + 左右 ~15° 3D 旋转 → rough.js 手绘高亮(在文字后,multiply)打在 Tesseract 定位的词上、左→右扫入。

## 文件
- `ArticleHighlight.tsx` —— 合成本体(读 `highlights.json` 定位高亮)。
- `Root.tsx` / `index.ts` —— 注册合成(1920×1080 / 30fps / 150 帧)。
- `highlights.json` —— OCR 出的词框(原图 px)+ 每个高亮的 `start` 帧。
- `public/article.png` —— 样例文章图(**替身**,含 "government shutdown"/"funding lapses";换成你的真图即可)。
- `package.json` —— 依赖(remotion / roughjs / react…)。

## 跑(放进一个 Remotion 工程里)
```bash
# 1) 一个 Remotion 工程(无则建),把本目录的 *.tsx/index.ts 放进 src/、article.png 放进 public/
npx create-video@latest --yes --blank --no-tailwind myvid && cd myvid
cp <本目录>/ArticleHighlight.tsx <本目录>/Root.tsx <本目录>/index.ts src/
cp <本目录>/highlights.json src/ ; cp <本目录>/public/article.png public/
npm install roughjs            # 按 package-lock.json → npm

# 2) 渲染(自动用干净 headless-shell,见 ../../scripts/render.sh)
bash ../../scripts/render.sh ArticleHighlight out/article.mp4
```

## 换成你的图
1. 你的图 → `public/article.png`
2. `python ../../scripts/ocr-to-highlights.py public/article.png "词1" "词2" --out src/highlights.json`
3. 重渲。合成代码不用动(全读 `highlights.json`)。

详见 `../../references/recipe-article-highlight.md` 和 `../../references/remotion-gotchas.md`。
