# 前端设计资源 · 借鉴入口（做片时来这找参考）

> 🔴 **借鉴铁律(先懂这条)**：这些是**网页**资源。**外观 / 结构 / 审美方向能借;动效本身不能直接搬**——视频是逐帧渲染,CSS transition / framer-motion / requestAnimationFrame / 滚动·hover 触发的动效**渲染时是死的**。要那个效果,就在**帧时钟上重写**(Remotion `interpolate(useCurrentFrame(),…)`;HF 用 GSAP timeline)。
> 一句话:**借"长什么样"和"动效创意",不借"会自己动的代码"。**

## A. 组件库(借外观 + 借动效创意)
| 站 | 入口 | 借什么 / 注意 |
|---|---|---|
| **shadcn** | ui.shadcn.com · github.com/topics/shadcn | **无动效结构组件**(卡片/按钮/表格/徽章)——做拟真界面**直接搬**(Remotion 本就是 React,可直接 import) |
| **Aceternity UI** | ui.aceternity.com | 聚光 spotlight / 光束 beams / 卡片堆 / 文字特效等炫组件——借**外观+创意**,动效用 interpolate 重写 |
| **React Bits** | reactbits.dev | 文字动效 / 背景动效的**创意库**——同上,重写到帧时钟。本机还有 `reactbits-animator` 技能 |
| **21st.dev** | 21st.dev | 精挑的 React 组件/模板(非 AI 生成),质量高 |

## B. 灵感库(定调:配色/版式/构图,**不是代码**)
| 站 | 入口 | 用法 |
|---|---|---|
| **Awwwards** | awwwards.com | 最佳网页设计趋势,定"高级感"方向 |
| **Land-book** | land-book.com | 落地页设计灵感库 |
| **Siteinspire** | siteinspire.com | 精选网站灵感 |
| **onepagelove** | onepagelove.com | 单页设计参考 |
| **landing.love** | landing.love | 落地页**动效**灵感(借节奏/点子) |
| **inja** | (见浏览器书签) | 落地页设计灵感 |

## 怎么用(两步)
1. **定调**：做片前去 B 挑 1-2 个方向(配色/版式/构图/字体),喂给 `taste-skill` / `impeccable` / Claude Design 落成规范。
2. **取件**：去 A 挑具体效果 → **外观照搬**(Remotion 直接用 shadcn/Aceternity 的 JSX 结构)→ **动效用 `interpolate`/`spring` 重写**(别指望它原生动)。

> 是「验证过的起点/灵感源」,不是上限。挑中某个效果想沉淀成配方 → 重写好、渲染验证过,再进配方菜单。
