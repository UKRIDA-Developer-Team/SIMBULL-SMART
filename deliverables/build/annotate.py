"""Draw numbered callouts on the app screenshots for the User Manual.

Input : deliverables/user-manual/screens/*.png + *.json (element boxes captured in the browser)
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
    blank = [gray.crop((0, y, w, y + 1)).getextrema()[0] > 240 for y in range(h)]
    parts, top, k = [], 0, 0
    while top < h:
        cut = min(top + max_h, h)
        if cut < h:
            for y in range(cut, max(top + max_h // 2, cut - 600), -1):
                if all(blank[y - 14:y + 1]):
                    cut = y
                    break
        k += 1
        part = name.replace(".png", f"_{chr(96 + k)}.png")
        img.crop((0, top, w, cut)).save(FIGS / part, optimize=True)
        parts.append(part)
        top = cut
    (FIGS / name).unlink()
    return parts


def main():
    home = boxes("01_home.json")
    annotate("01_home.png", "fig01_home.png", [
        (1, home["nav"]), (2, home["lang"]), (3, home["profile"]), (4, home["badge"]),
        (5, home["disclaimer"]), (6, home["metrics"]), (7, home["flow"])])

    form = boxes("02_reco_form.json")
    annotate("02_reco_form.png", "fig02_form_top.png", [
        (1, form["tabs"]), (2, form["mode"]), (3, form["examples"]), (4, form["identity"]),
        (5, form["slider"]), (6, form["grade"])], crop=(0, 330, None, 1150))
    annotate("02_reco_form.png", "fig03_form_submit.png", [(7, form["submit"])], crop=(0, 1900, None, 2380))

    res = boxes("03_reco_result.json")
    top = res["divider_y"] - 10
    annotate("03_reco_result_full.png", "fig04_result.png", [
        (1, res["safety"]), (2, res["metrics"]), (3, res["help"]), (4, res["cards"]),
        (5, res["why"]), (6, res["chart"])], crop=(0, top, None, res["exp_inputs"][1] - 10))
    annotate("03_reco_result_full.png", "ppt_result_top.png", [],
             crop=(100, res["safety"][1] - 20, 1550, res["cards"][1] + res["cards"][3] + 20))
    annotate("03_reco_result_full.png", "ppt_contrib.png", [],
             crop=(100, res["chart"][1] - 10, 1550, res["chart"][1] + res["chart"][3] + 10))
    annotate("04_reco_inputs.png", "fig05_inputs.png", [])
    annotate("05_reco_sensitivity.png", "fig06_sensitivity.png", [])

    batch = boxes("06_reco_batch.json")
    eval_y = batch["eval"][1]
    annotate("06_reco_batch_full.png", "fig07_batch_a.png", [
        (1, batch["upload"]), (2, batch["demo"]), (3, batch["detected"]), (4, batch["bounds"]),
        (5, batch["topn"]), (6, batch["table"]), (7, batch["download"]), (8, batch["charts"])],
        crop=(0, 360, None, eval_y - 30))
    annotate("06_reco_batch_full.png", "fig07_batch_b.png", [(9, batch["eval"])],
             crop=(0, eval_y - 40, None, 100000))

    tabs = boxes("07_an.json")["tabs"]
    annotate("07_an_data.png", "fig08_an_data.png", [(1, tabs)], crop=(0, 120, None, 1980))
    for i, name in enumerate(["08_an_model", "09_an_smart", "10_an_sens", "11_an_fair"], start=9):
        annotate(f"{name}.png", f"fig{i:02d}_{name[3:]}.png", [], crop=(0, 120, None, 100000))
    annotate("12_about.png", "fig13_about.png", [], crop=(0, 120, None, 100000))
    annotate("13_en_view.png", "fig14_en.png", [(1, boxes("13_en.json")["lang"])])
    for name in ["fig09_an_model.png", "fig10_an_smart.png", "fig11_an_sens.png", "fig13_about.png"]:
        print(name, "->", split_tall(name))
    print("figures ->", FIGS)


if __name__ == "__main__":
    main()
