"""Draw numbered callouts on the app screenshots for the User Manual.

Input : deliverables/user-manual/screens/*.png + *.json (element boxes, from capture_screens.js)
Output: deliverables/user-manual/figures/*.png

Run with any Python that has Pillow (e.g. app/.venv/bin/python deliverables/build/annotate.py).
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1] / "user-manual"
SCREENS, FIGS = ROOT / "screens", ROOT / "figures"
RED = (220, 38, 38)


def font(size):
    for name in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def boxes(name):
    return json.loads((SCREENS / name).read_text())


def annotate(src, out, marks, crop=None, pad=6):
    """marks: list of (number, [x, y, w, h]) in source-pixel coordinates."""
    img = Image.open(SCREENS / src).convert("RGB")
    draw = ImageDraw.Draw(img)
    f = font(30)
    for n, (x, y, w, h) in marks:
        draw.rounded_rectangle([x - pad, y - pad, x + w + pad, y + h + pad], radius=10, outline=RED, width=4)
        r = 22
        cx, cy = max(x - pad, r + 2), max(y - pad, r + 2)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
        draw.text((cx, cy), str(n), fill="white", font=f, anchor="mm")
    if crop:
        x0, y0, x1, y1 = crop
        img = img.crop((x0, max(0, y0), x1 or img.width, min(img.height, y1)))
    FIGS.mkdir(parents=True, exist_ok=True)
    img.save(FIGS / out, optimize=True)
    return out


def split_tall(name, max_h=2000):
    """Cut a tall figure into parts at blank (near-white) rows so each part fits a page."""
    img = Image.open(FIGS / name).convert("RGB")
    if img.height <= max_h * 1.15:
        return [name]
    gray = img.convert("L")
    w, h = gray.size
    # Prefer a gap between cards (blank across the full width); otherwise a gap between two lines inside a
    # bordered card (blank in the middle band, which leaves out the card's side borders).
    x0, x1 = int(w * 0.06), int(w * 0.94)
    gaps = [[gray.crop((0, y, w, y + 1)).getextrema()[0] > 240 for y in range(h)],
            [gray.crop((x0, y, x1, y + 1)).getextrema()[0] > 240 for y in range(h)]]
    parts, top, k = [], 0, 0
    while top < h:
        cut = min(top + max_h, h)
        if h - cut < max_h * 0.3:          # a short tail joins this part instead of standing alone
            cut = h
        if cut < h:
            found = (y for blank in gaps for y in range(cut, max(top + max_h // 2, cut - 600), -1)
                     if all(blank[y - 14:y + 1]))
            cut = next(found, cut)
        k += 1
        part = name.replace(".png", f"_{chr(96 + k)}.png")
        img.crop((0, top, w, cut)).save(FIGS / part, optimize=True)
        parts.append(part)
        top = cut
    (FIGS / name).unlink()
    return parts


def column(b, top, bottom, margin=44):
    """Crop box for the page's content column (boxes json key "content") between two y values."""
    x, _, w, _ = b["content"]
    return (x - margin, top, x + w + margin, bottom)


def bottom(box, gap=0):
    return box[1] + box[3] + gap


def inset(box, dx=16, dy=0):
    """Shrink a box so callouts on side-by-side parts of one card do not overlap."""
    x, y, w, h = box
    return [x + dx, y + dy, w - 2 * dx, h - 2 * dy]


def main():
    # ================================================================ App zone
    home = boxes("01_home.json")
    annotate("01_home.png", "fig01_home.png", [
        (1, home["nav"]), (2, home["zone"]), (3, home["lang"]), (4, home["cta"]), (5, home["cta_batch"]),
        (6, home["preview"]), (7, home["steps"]), (8, home["alts"]), (9, home["report"]), (10, home["footer"])],
        crop=(0, 0, None, bottom(home["footer"], 30)))

    form = boxes("02_form.json")
    annotate("02_form.png", "fig02_form_top.png", [
        (1, form["model"]), (2, form["q1"]), (3, form["select"]), (4, form["grade"]), (5, form["radio"]),
        (6, form["tips"]), (7, form["examples"]), (8, form["clear"])],
        crop=column(form, form["title"][1] - 40, bottom(form["q2"], 40)))
    annotate("02_form.png", "fig03_form_submit.png", [(9, form["submit"])],
             crop=column(form, form["q5"][1] - 40, bottom(form["submit"], 40)))
    miss = boxes("03_missing.json")
    annotate("03_missing.png", "fig03b_missing.png", [(1, miss["missing"])],
             crop=column(miss, miss["submit"][1] - 30, bottom(miss["missing"], 40)))

    model = boxes("04_model.json")
    body, button = model["body"], model["button"]
    annotate("04_model.png", "fig04_model.png", [(1, button), (2, model["radio"]), (3, model["note"])],
             crop=(body[0] - 44, button[1] - 24, button[0] + button[2] + 44, bottom(body, 40)))

    ex = boxes("05_example.json")
    annotate("05_example.png", "fig05_example.png", [(1, ex["loaded"]), (2, ex["q1"]), (3, ex["examples"])],
             crop=column(ex, ex["title"][1] - 40, bottom(ex["q1"], 40)))

    res = boxes("06_result.json")
    annotate("06_result.png", "fig06_result.png", [
        (1, res["back"]), (2, res["safety"]), (3, inset(res["best"])), (4, inset(res["anx"])),
        (5, inset(res["prio"])), (6, res["rank"]), (7, res["why"]), (8, res["factors"]), (9, res["whatif"]),
        (10, res["cta"]), (11, res["next"])],
        crop=column(res, res["back"][1] - 40, bottom(res["next"], 40)))
    annotate("06_result.png", "ppt_result_top.png", [],
             crop=column(res, res["safety"][1] - 16, bottom(res["hero"], 16), margin=12))
    annotate("06_result.png", "ppt_result_xai.png", [],
             crop=column(res, res["factors"][1] - 16, bottom(res["whatif"], 16), margin=12))

    wi = boxes("07_whatif.json")
    x, y, w, h = wi["whatif"]
    annotate("07_whatif.png", "fig07_whatif.png", [(1, wi["pick"]), (2, wi["sliders"]), (3, wi["out"])],
             crop=(x - 40, y - 40, x + w + 40, y + h + 40))

    cls = boxes("09_class_empty.json")
    annotate("09_class_empty.png", "fig09_class_empty.png", [
        (1, cls["upload"]), (2, cls["toggle"]), (3, cls["template"]), (4, cls["empty"])],
        crop=column(cls, cls["title"][1] - 40, bottom(cls["empty"], 40)))
    c = boxes("10_class.json")
    annotate("10_class.png", "fig10_class_a.png", [
        (1, c["note"]), (2, c["metrics"]), (3, c["urgent"]), (4, c["filters"]), (5, c["table"]), (6, c["download"])],
        crop=column(c, c["note"][1] - 36, bottom(c["download"], 40)))
    annotate("10_class.png", "fig10_class_b.png", [(7, c["programs"]), (8, c["one"]), (9, c["options"])],
             crop=column(c, c["programs"][1] - 150, bottom(c["options"], 40)))

    hlp = boxes("11_help.json")
    annotate("11_help.png", "fig11_help.png", [(1, hlp["use"]), (2, hlp["read"]), (3, hlp["notes"])],
             crop=column(hlp, hlp["title"][1] - 40, hlp["footer"][1] - 20))

    # ================================================================ Report zone
    ch1 = boxes("12_ch1.json")
    annotate("12_ch1.png", "fig12_report_frame.png", [
        (1, ch1["zone"]), (2, ch1["nav"]), (3, ch1["eyebrow"]), (4, ch1["toc"]), (5, ch1["model"]),
        (6, ch1["h"]), (7, ch1["cap"])],
        crop=(0, 0, None, bottom(ch1["cap"], 60)))
    annotate("12_ch1.png", "fig12b_pager.png", [(8, ch1["pager"])],
             crop=column(ch1, ch1["pager"][1] - 60, bottom(ch1["pager"], 40)))
    annotate("12_ch1.png", "fig13_ch1.png", [], crop=column(ch1, ch1["title"][1] - 40, ch1["footer"][1] - 20))

    ch3 = boxes("08_ch3.json")
    annotate("08_ch3.png", "fig14_ch3_top.png", [(1, ch3["toc"]), (2, ch3["source"]), (3, ch3["cap"])],
             crop=column(ch3, ch3["eyebrow"][1] - 40, ch3["s4"][1] - 20))
    for out, top, end in [("fig15_ch3_utility.png", "s4", "s6"), ("fig16_ch3_scores.png", "s6", "s8"),
                          ("fig17_ch3_priority.png", "s8", "s10"), ("fig18_ch3_xai.png", "s10", "footer")]:
        annotate("08_ch3.png", out, [], crop=column(ch3, ch3[top][1] - 30, ch3[end][1] - 20))

    for src, out in [("13_ch2", "fig19_ch2.png"), ("14_ch4", "fig20_ch4.png"), ("15_ch5", "fig21_ch5.png"),
                     ("16_ch6", "fig22_ch6.png"), ("19_ch8", "fig25_ch8.png")]:
        b = boxes(f"{src}.json")
        annotate(f"{src}.png", out, [], crop=column(b, b["title"][1] - 40, b["footer"][1] - 20))

    dm = boxes("17_ch7.json")
    annotate("17_ch7.png", "fig23_ch7.png", [
        (1, dm["stepper"]), (2, dm["hero"]), (3, dm["kpis"]), (4, dm["steps"]), (5, dm["main"]),
        (6, dm["side"]), (7, dm["next"])],
        crop=column(dm, dm["title"][1] - 40, bottom(dm["next"], 40)))
    prep = boxes("18_ch7_prep.json")
    annotate("18_ch7_prep.png", "fig24_ch7_prep.png", [(1, prep["kpis"]), (2, prep["merge"])],
             crop=column(prep, prep["hero"][1] - 30, bottom(prep["side"], 40)))

    en = boxes("20_en.json")
    annotate("20_en.png", "fig26_en.png", [(1, en["zone"]), (2, en["lang"]), (3, en["nav"])], crop=(0, 0, None, 1180))

    for name in ["fig10_class_a.png", "fig11_help.png", "fig13_ch1.png", "fig15_ch3_utility.png",
                 "fig16_ch3_scores.png", "fig17_ch3_priority.png", "fig18_ch3_xai.png", "fig19_ch2.png",
                 "fig20_ch4.png", "fig21_ch5.png", "fig22_ch6.png", "fig24_ch7_prep.png", "fig25_ch8.png"]:
        print(name, "->", split_tall(name))
    print("figures ->", FIGS)


if __name__ == "__main__":
    main()
