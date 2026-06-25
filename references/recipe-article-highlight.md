# 配方：文章图 OCR 高亮（验证过的范例逐步拆解）

成片效果：白底全高清上居中一张文章图 → 开头整体模糊、1秒内渐清 → 5秒内极轻微缩放 + 左右各 ~15° 的 3D 旋转 → 模糊完后,在 OCR 定位到的词上用 rough.js 画手绘高亮(在文字后面)、左→右扫入。源工程见 `examples/article-highlight/`。

## 步骤
1. **图进 `public/`**，记下原图像素宽高(范例 1100×1420)。
2. **OCR 出坐标**：
   ```bash
   python scripts/ocr-to-highlights.py public/article.png "government shutdown" "funding lapses" \
       --out src/highlights.json
   ```
   产出 `highlights.json`：`{imageWidth, imageHeight, phrases:[{text,x,y,w,h,start}]}`(框是**原图 px**,`start` 是该高亮开始扫入的帧号)。
3. **合成**(`ArticleHighlight.tsx`)关键参数,按需改:
   - 画布：1920×1080 / 30fps / 150 帧(=5s)。
   - 显示：`DISPLAY_H=940` → `S=DISPLAY_H/imageHeight`,所有 OCR 框 × S 映射到画面。
   - 模糊渐清：`interpolate(frame,[0,30],[16,0],{easing:Easing.out(Easing.cubic),extrapolateRight:'clamp'})`。
   - 微缩放：`interpolate(frame,[0,150],[1,1.05])`。
   - 左右旋转(~15°/轴)：`rotateY: [-7.5,7.5]`、`rotateX: [6,-6]`,容器加 `perspective:1700` + `transformStyle:'preserve-3d'`。
   - 高亮：每个 phrase 一个绝对定位 div(`left/top/width/height` = 框×S),`mixBlendMode:'multiply'`,内嵌 `<canvas>` 用 `rough.canvas(c).rectangle(...,{fill:'#ffd84a',fillStyle:'solid',stroke:'none',seed:7+i})`;外层 div 的 `width = w*reveal`、`overflow:hidden` → 左→右扫入,`reveal=interpolate(frame,[start,start+13],[0,1],{easing:Easing.out(Easing.cubic),clamp})`。
4. **渲染**：`bash scripts/render.sh ArticleHighlight out.mp4`。

## 想改成你的图
1. 你的图 → `public/article.png`(或改 `staticFile` 名)。
2. 重跑第 2 步 OCR(换成你图里要高亮的词);`ocr-to-highlights.py` 会自动写新的 `imageWidth/Height` + 框。
3. 重渲。**合成代码基本不用动**(它全读 `highlights.json`)。

## 可玩的变体(照用法哲学自由生成)
- 高亮换**圈注/下划线/箭头**:rough.js 还能 `circle`/`line`/`linearPath`,同样 multiply。
- 多张图轮播 + 每张各自 OCR:每张一个 `<Sequence>`,接缝用 `@remotion/transitions`。
- 参数化:把图名/词/配色提成 Zod schema(见 `remotion-best-practices` 的 parameters.md),`--props` 批量出片。
- 实拍/录屏打底:把 `<Img>` 换 `<OffthreadVideo>`,高亮浮在视频上(注意 OCR 是针对静帧的,动视频要按时间取帧定位)。
