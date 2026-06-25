#!/usr/bin/env python3
"""Run Tesseract OCR on an image and write highlights.json of phrase bounding
boxes (native image px) for the vibemotion-remotion article-highlight composition.

Usage:
  python ocr-to-highlights.py IMAGE "phrase one" "phrase two" [--out src/highlights.json]
                              [--starts 34,52] [--first-start 34 --gap 18]
                              [--occurrence last|first|N]

Requires: tesseract CLI. Pillow is OPTIONAL — PNG size is read with the stdlib;
non-PNG images fall back to Pillow.

Gotchas this handles (learned the hard way):
 - Tesseract 5.x writes `conf` as a FLOAT string (e.g. "96.0") → parse via float,
   NOT int (int("96.0") raises and silently drops every word → 0 matches).
 - A phrase can appear more than once (headline + body). Default picks the match
   furthest DOWN the page (`--occurrence last`, usually the body, not the headline);
   pass --occurrence first|N to choose. Multiple matches are printed as a WARN.
 - Exits non-zero if any phrase isn't placed, so batch pipelines fail loudly
   instead of silently rendering a clip with no highlights.
"""
import argparse, csv, io, json, re, struct, subprocess, sys
from pathlib import Path


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(26)
    if head[:8] == b"\x89PNG\r\n\x1a\n" and head[12:16] == b"IHDR":
        w, h = struct.unpack(">II", head[16:24])
        return int(w), int(h)
    return None


def img_size(path):
    s = png_size(path)
    if s:
        return s
    from PIL import Image  # optional fallback for non-PNG
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
            if float(d["conf"]) < 0:   # Tesseract 5.x conf is a float string
                continue
        except (ValueError, KeyError, TypeError):
            continue
        rows.append({"line": (d["block_num"], d["par_num"], d["line_num"]),
                     "l": int(d["left"]), "t": int(d["top"]),
                     "w": int(d["width"]), "h": int(d["height"]), "txt": t})
    return rows


def find_all(rows, phrase):
    seq = [norm(w) for w in phrase.split()]
    hits = []
    for i in range(len(rows) - len(seq) + 1):
        win = rows[i:i + len(seq)]
        if all(norm(win[k]["txt"]) == seq[k] for k in range(len(seq))) \
           and len({w["line"] for w in win}) == 1:
            xs = [w["l"] for w in win]
            ys = [w["t"] for w in win]
            rt = [w["l"] + w["w"] for w in win]
            bt = [w["t"] + w["h"] for w in win]
            hits.append({"x": min(xs), "y": min(ys), "w": max(rt) - min(xs), "h": max(bt) - min(ys)})
    return hits


def pick(hits, occurrence):
    if occurrence == "first":
        return hits[0]
    if occurrence == "last":
        return max(hits, key=lambda b: b["y"])   # furthest down = usually the body
    idx = int(occurrence) - 1
    return hits[idx] if 0 <= idx < len(hits) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("phrases", nargs="+")
    ap.add_argument("--out", default="highlights.json")
    ap.add_argument("--starts", default=None, help="comma-separated start frames, one per phrase")
    ap.add_argument("--first-start", type=int, default=34)
    ap.add_argument("--gap", type=int, default=18)
    ap.add_argument("--occurrence", default="last",
                    help="which match to use when a phrase appears >1x: last (default, ~body), first, or 1-based N")
    a = ap.parse_args()

    W, H = img_size(a.image)
    rows = ocr_rows(a.image)
    if not rows:
        print("ERROR: OCR returned 0 words — is tesseract installed and the image readable?", file=sys.stderr)
        sys.exit(2)

    starts = [int(x) for x in a.starts.split(",")] if a.starts else \
             [a.first_start + i * a.gap for i in range(len(a.phrases))]

    phrases, missing = [], []
    for i, ph in enumerate(a.phrases):
        hits = find_all(rows, ph)
        if not hits:
            print(f"  MISS {ph!r}: not found (check OCR read / spelling / try a clearer image)", file=sys.stderr)
            missing.append(ph)
            continue
        if len(hits) > 1:
            ys = ", ".join(f"#{j+1}@y{h['y']}" for j, h in enumerate(sorted(hits, key=lambda b: b['y'])))
            print(f"  WARN {ph!r}: {len(hits)} matches ({ys}); using --occurrence={a.occurrence}", file=sys.stderr)
        box = pick(hits, a.occurrence)
        if box is None:
            print(f"  MISS {ph!r}: --occurrence={a.occurrence} out of range (1..{len(hits)})", file=sys.stderr)
            missing.append(ph)
            continue
        start = starts[i] if i < len(starts) else a.first_start + i * a.gap
        phrases.append({"text": ph, "start": start, **box})
        print(f"  ok  {ph!r} -> {box} (start {start})")

    out = {"imageWidth": W, "imageHeight": H, "phrases": phrases}
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"wrote {a.out} ({len(phrases)}/{len(a.phrases)} phrases)")
    if missing:
        print(f"FAIL: {len(missing)} phrase(s) not placed: {missing}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
