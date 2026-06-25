import {
  AbsoluteFill,
  Img,
  staticFile,
  useCurrentFrame,
  interpolate,
  Easing,
} from "remotion";
import { useEffect, useRef } from "react";
import rough from "roughjs";
import data from "./highlights.json";

const DISPLAY_H = 940; // article displayed height on the 1080 canvas
const S = DISPLAY_H / data.imageHeight;
const DISPLAY_W = data.imageWidth * S;

type Phrase = { text: string; x: number; y: number; w: number; h: number; start: number };

// One rough.js highlighter mark, swept in left→right, sitting BEHIND the text (multiply blend)
const Highlight: React.FC<{ p: Phrase; index: number }> = ({ p, index }) => {
  const frame = useCurrentFrame();
  const ref = useRef<HTMLCanvasElement>(null);
  // pad a touch so the marker is slightly taller than the text, like a real highlighter
  const padY = p.h * 0.18;
  const x = p.x * S;
  const y = (p.y - padY) * S;
  const w = p.w * S;
  const h = (p.h + padY * 2) * S;

  // left→right reveal after the blur is done
  const reveal = interpolate(frame, [p.start, p.start + 13], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  useEffect(() => {
    const c = ref.current;
    if (!c) return;
    const ctx = c.getContext("2d");
    if (!ctx) return;
    ctx.clearRect(0, 0, c.width, c.height);
    const rc = rough.canvas(c);
    rc.rectangle(2, 2, w - 4, h - 4, {
      fill: "#ffd84a",
      fillStyle: "solid",
      stroke: "none",
      roughness: 1.6,
      bowing: 1.2,
      seed: 7 + index, // fixed seed → deterministic across frames
    });
  }, [w, h, index]);

  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: w * reveal,
        height: h,
        overflow: "hidden",
        mixBlendMode: "multiply", // dark text stays on top, white bg turns yellow → "behind text"
      }}
    >
      <canvas
        ref={ref}
        width={Math.ceil(w)}
        height={Math.ceil(h)}
        style={{ width: w, height: h, display: "block" }}
      />
    </div>
  );
};

export const ArticleHighlight: React.FC = () => {
  const frame = useCurrentFrame();

  // blur the whole composition, un-blur over the first second (0→30 frames)
  const blur = interpolate(frame, [0, 30], [16, 0], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // very subtle, slow zoom over the 5s
  const scale = interpolate(frame, [0, 150], [1, 1.05]);
  // slight left→right rotation, ~15° total per axis
  const rotateY = interpolate(frame, [0, 150], [-7.5, 7.5]);
  const rotateX = interpolate(frame, [0, 150], [6, -6]);

  return (
    <AbsoluteFill style={{ backgroundColor: "#ffffff" }}>
      <AbsoluteFill
        style={{ justifyContent: "center", alignItems: "center", perspective: 1700 }}
      >
        <div
          style={{
            width: DISPLAY_W,
            height: DISPLAY_H,
            position: "relative",
            filter: `blur(${blur}px)`,
            transform: `scale(${scale}) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
            transformStyle: "preserve-3d",
            boxShadow: "0 30px 90px rgba(0,0,0,0.14)",
          }}
        >
          <Img
            src={staticFile("article.png")}
            style={{ width: DISPLAY_W, height: DISPLAY_H, display: "block" }}
          />
          {(data.phrases as Phrase[]).map((p, i) => (
            <Highlight key={i} p={p} index={i} />
          ))}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
