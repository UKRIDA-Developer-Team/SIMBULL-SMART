"""Render a .docx/.pptx to page PNGs with ONLYOFFICE x2t, then tile them into contact sheets.

    python deliverables/build/preview.py <file> <out_dir> [pages_per_sheet=6] [page_width=900]
"""
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from PIL import Image

X2T = "/Applications/ONLYOFFICE.app/Contents/Resources/converter/x2t"
FONTS = Path.home() / "Library/Application Support/asc.onlyoffice.ONLYOFFICE/data/fonts"


def render(src: Path, out_dir: Path, width: int) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    zpath = out_dir / (src.stem + ".zip")
    is_ppt = src.suffix.lower() == ".pptx"
    height = int(width * (9 / 16 if is_ppt else 297 / 210))
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<TaskQueueDataConvert xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<m_sFileFrom>{src.resolve()}</m_sFileFrom><m_sFileTo>{zpath.resolve()}</m_sFileTo><m_nFormatTo>1029</m_nFormatTo>
<m_sAllFontsPath>{FONTS}/AllFonts.js</m_sAllFontsPath><m_sFontDir>{FONTS}</m_sFontDir><m_bIsNoBase64>true</m_bIsNoBase64>
<m_oThumbnail><format>4</format><aspect>1</aspect><first>false</first><width>{width}</width><height>{height}</height></m_oThumbnail>
</TaskQueueDataConvert>"""
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write(xml)
    subprocess.run([X2T, f.name], capture_output=True)
    pages_dir = out_dir / src.stem
    with zipfile.ZipFile(zpath) as z:
        z.extractall(pages_dir)
    return sorted(pages_dir.glob("image*.png"), key=lambda p: int(re.findall(r"\d+", p.stem)[0]))


def sheets(pages: list[Path], out_dir: Path, per: int, stem: str) -> list[Path]:
    out = []
    cols = 3 if per >= 6 else 2
    for s in range(0, len(pages), per):
        imgs = [Image.open(p).convert("RGB") for p in pages[s:s + per]]
        w, h = imgs[0].size
        rows = (len(imgs) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * w + (cols + 1) * 10, rows * h + (rows + 1) * 10), (120, 120, 120))
        for k, im in enumerate(imgs):
            sheet.paste(im, (10 + (k % cols) * (w + 10), 10 + (k // cols) * (h + 10)))
        path = out_dir / f"{stem}_sheet{s // per + 1:02d}.png"
        sheet.save(path)
        out.append(path)
    return out


if __name__ == "__main__":
    src, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    per = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    width = int(sys.argv[4]) if len(sys.argv) > 4 else 900
    pages = render(src, out_dir, width)
    print(len(pages), "pages")
    for p in sheets(pages, out_dir, per, src.stem):
        print(p)
