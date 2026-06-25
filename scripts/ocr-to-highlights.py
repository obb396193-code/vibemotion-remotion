#!/usr/bin/env python3
"""Run Tesseract OCR on an image and write a highlights.json of phrase bounding
boxes (native image px) for the vibemotion-remotion article-highlight composition.

Usage:
  python ocr-to-highlights.py IMAGE "phrase one" "phrase two" [--out src/highlights.json]
                              [--starts 34,52] [--first-start 34 --gap 18]

Requires: tesseract CLI (brew install tesseract) + Pillow (pip install pillow).
Notes: uses default psm (layout analysis) — do NOT force --psm 6 on multi-region
articles, it jumbles line order. Matches consecutive words on the SAME line.
"""
import argparse, csv, io, json, re, subprocess, sys
from pathlib import Path


def img_size(path):
    from PIL import Image
    with Image.open(path) as im:
        return im.size


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def ocr_rows(path):
    out = subprocess.run(["tesseract", str(path), "stdout", "tsv"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit("tesseract failed:\n" + out.stderr)
    rows = []
    for d in csv.DictReader(io.StringIO(out.stdout), delimiter="\t"):
        t = (d.get("text") or "").strip()
        if not t:
            continue
        try:
            if int(d["conf"]) < 0:
                continue
        except (ValueError, KeyError):
            continue
        rows.append({"line": (d["block_num"], d["par_num"], d["line_num"]),
                     "l": int(d["left"]), "t": int(d["top"]),
                     "w": int(d["width"]), "h": int(d["height"]), "txt": t})
    return rows


def find_phrase(rows, phrase):
    seq = [norm(w) for w in phrase.split()]
    for i in range(len(rows) - len(seq) + 1):
        win = rows[i:i + len(seq)]
        if all(norm(win[k]["txt"]) == seq[k] for k in range(len(seq))) \
           and len({w["line"] for w in win}) == 1:
            xs = [w["l"] for w in win]
            ys = [w["t"] for w in win]
            rt = [w["l"] + w["w"] for w in win]
            bt = [w["t"] + w["h"] for w in win]
            return {"x": min(xs), "y": min(ys), "w": max(rt) - min(xs), "h": max(bt) - min(ys)}
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("phrases", nargs="+")
    ap.add_argument("--out", default="highlights.json")
    ap.add_argument("--starts", default=None, help="comma-separated start frames, one per phrase")
    ap.add_argument("--first-start", type=int, default=34)
    ap.add_argument("--gap", type=int, default=18)
    a = ap.parse_args()

    W, H = img_size(a.image)
    rows = ocr_rows(a.image)
    starts = [int(x) for x in a.starts.split(",")] if a.starts else \
             [a.first_start + i * a.gap for i in range(len(a.phrases))]

    phrases = []
    for i, ph in enumerate(a.phrases):
        box = find_phrase(rows, ph)
        if not box:
            print(f"  WARN not found: {ph!r} (check OCR read / spelling)", file=sys.stderr)
            continue
        start = starts[i] if i < len(starts) else a.first_start + i * a.gap
        phrases.append({"text": ph, "start": start, **box})
        print(f"  ok {ph!r} -> {box} (start {start})")

    out = {"imageWidth": W, "imageHeight": H, "phrases": phrases}
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"wrote {a.out} ({len(phrases)}/{len(a.phrases)} phrases)")


if __name__ == "__main__":
    main()
