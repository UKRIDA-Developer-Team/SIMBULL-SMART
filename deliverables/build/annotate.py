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
    home = boxes("01_home.json")
    annotate("01_home.png", "fig01_home.png", [
        (1, home["nav"]), (2, home["lang"]), (3, home["cta"]), (4, home["cta_batch"]), (5, home["preview"]),
        (6, home["steps"]), (7, home["alts"]), (8, home["notes"]), (9, home["footer"])],
        crop=(0, 0, None, bottom(home["footer"], 30)))

    form = boxes("02_reco_form.json")
    annotate("02_reco_form.png", "fig02_form_top.png", [
        (1, form["view"]), (2, form["profile"]), (3, form["adv"]), (4, form["q1"]), (5, form["slider"]),
        (6, form["grade"]), (7, form["radio"]), (8, form["tips"]), (9, form["examples"])],
        crop=column(form, form["title"][1] - 40, bottom(form["q2"], 40)))
    annotate("02_reco_form.png", "fig03_form_submit.png", [(10, form["submit"])],
             crop=column(form, form["q5"][1] - 40, bottom(form["submit"], 40)))

    res = boxes("04_result.json")
    annotate("04_result.png", "fig04_result.png", [
        (1, res["back"]), (2, res["reset"]), (3, res["safety"]),
        (4, inset(res["best"])), (5, inset(res["anx"])), (6, inset(res["prio"])),
        (7, res["rank"]), (8, res["why"]), (9, res["compare"]), (10, res["xai"]), (11, res["details"])],
        crop=column(res, res["back"][1] - 40, bottom(res["details"], 40)))
    annotate("04_result.png", "ppt_result_top.png", [],
             crop=column(res, res["safety"][1] - 16, bottom(res["hero"], 16), margin=12))

    cmp = boxes("04b_compare.json")
    annotate("04b_compare.png", "fig04b_compare.png", [], crop=column(cmp, cmp["compare"][1] - 30, bottom(cmp["compare"], 30)))

    for n, (src, out) in enumerate([("05_xai_pred", "fig05_xai_pred.png"), ("06_xai_link", "fig06_xai_link.png"),
                                    ("07_xai_whatif", "fig07_xai_whatif.png")], start=1):
        b = boxes(f"{src}.json")
        annotate(f"{src}.png", out, [(1, b["tabs"])], crop=column(b, b["xai"][1] - 40, bottom(b["xai"], 40)))
    link = boxes("06_xai_link.json")
    x, y, w, h = link["chart"]
    annotate("06_xai_link.png", "ppt_contrib.png", [], crop=(x - 10, y - 10, x + w + 10, y + h + 10))

    for src, out in [("08_details_inputs", "fig08_inputs.png"), ("09_details_sens", "fig09_sensitivity.png")]:
        b = boxes(f"{src}.json")
        annotate(f"{src}.png", out, [(1, b["tabs"])], crop=column(b, b["details"][1] - 40, bottom(b["details"], 40)))

    prof = boxes("03_profile.json")
    body, button = prof["body"], prof["button"]
    annotate("03_profile.png", "fig10_profile.png", [(1, button), (2, prof["model"]), (3, prof["radio"]), (4, prof["note"])],
             crop=(body[0] - 44, button[1] - 24, button[0] + button[2] + 44, bottom(body, 40)))

    batch = boxes("10_batch.json")
    annotate("10_batch.png", "fig11_batch_a.png", [
        (1, batch["upload"]), (2, batch["demo"]), (3, batch["metrics"]), (4, batch["list"]),
        (5, batch["table"]), (6, batch["download"])],
        crop=column(batch, batch["upload"][1] - 36, bottom(batch["download"], 40)))
    annotate("10_batch.png", "fig11_batch_b.png", [(7, batch["charts"]), (8, batch["xai"]), (9, batch["options"])],
             crop=column(batch, batch["charts"][1] - 40, bottom(batch["options"], 40)))

    data = boxes("11_an_data.json")
    annotate("11_an_data.png", "fig12_an_data.png", [(1, data["population"]), (2, data["profile"]), (3, data["tabs"])],
             crop=column(data, data["title"][1] - 40, data["footer"][1] - 20))
    for src, out in [("12_an_model", "fig13_an_model.png"), ("13_an_xai", "fig14_an_xai.png"),
                     ("14_an_smart", "fig15_an_smart.png"), ("15_an_sens", "fig16_an_sens.png"),
                     ("16_an_fair", "fig17_an_fair.png")]:
        b = boxes(f"{src}.json")
        annotate(f"{src}.png", out, [], crop=column(b, b["tabs"][1] - 30, b["footer"][1] - 20))

    dm = boxes("17_dm.json")
    annotate("17_dm.png", "fig18_dm.png", [
        (1, dm["stepper"]), (2, dm["hero"]), (3, dm["kpis"]), (4, dm["steps"]), (5, dm["main"]),
        (6, dm["side"]), (7, dm["next"])],
        crop=column(dm, dm["title"][1] - 40, bottom(dm["next"], 40)))
    prep = boxes("18_dm_prep.json")
    annotate("18_dm_prep.png", "fig19_dm_prep.png", [(1, prep["kpis"]), (2, prep["merge"])],
             crop=column(prep, prep["hero"][1] - 30, bottom(prep["side"], 40)))

    about = boxes("19_about.json")
    annotate("19_about.png", "fig20_about.png", [], crop=column(about, about["title"][1] - 40, about["footer"][1] - 20))
    en = boxes("20_en.json")
    annotate("20_en.png", "fig21_en.png", [(1, en["lang"]), (2, en["nav"])], crop=(0, 0, None, 1180))

    for name in ["fig12_an_data.png", "fig13_an_model.png", "fig14_an_xai.png", "fig15_an_smart.png",
                 "fig16_an_sens.png", "fig19_dm_prep.png", "fig20_about.png"]:
        print(name, "->", split_tall(name))
    print("figures ->", FIGS)


if __name__ == "__main__":
    main()
