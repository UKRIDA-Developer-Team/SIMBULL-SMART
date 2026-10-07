"""Tiny text extractor for the PDFs ONLYOFFICE x2t writes: returns the text of each page.

Only what the TOC step needs: page order, Flate streams, Tj/TJ strings and ToUnicode CMaps.
Usage: python pdf_pages.py file.pdf  -> prints "page<TAB>text" lines
"""
import re
import sys
import zlib

OBJ = re.compile(rb"(\d+) 0 obj(.*?)endobj", re.S)


def objects(data: bytes) -> dict[int, bytes]:
    return {int(n): body for n, body in OBJ.findall(data)}


def stream(body: bytes) -> bytes:
    m = re.search(rb"stream\r?\n(.*)\r?\nendstream", body, re.S)
    if not m:
        return b""
    raw = m.group(1)
    if b"/FlateDecode" in body:
        try:
            return zlib.decompress(raw)
        except zlib.error:
            return zlib.decompressobj().decompress(raw)
    return raw


def refs(body: bytes, key: bytes) -> list[int]:
    m = re.search(rb"/" + key + rb"\s*(\[[^\]]*\]|\d+ 0 R)", body)
    return [int(x) for x in re.findall(rb"(\d+) 0 R", m.group(1))] if m else []


def cmap(data: bytes) -> dict:
    """ToUnicode CMap -> {code: text}; key "_w" holds the code width in hex digits."""
    space = re.search(rb"begincodespacerange\s*<([0-9A-Fa-f]+)>", data)
    out = {"_w": len(space.group(1)) if space else 4}
    for block in re.findall(rb"beginbfchar(.*?)endbfchar", data, re.S):
        for src, dst in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", block):
            out[int(src, 16)] = bytes.fromhex(dst.decode()).decode("utf-16-be", "ignore")
    for block in re.findall(rb"beginbfrange(.*?)endbfrange", data, re.S):
        for a, b, dst in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", block):
            start = int(dst, 16)
            for k, code in enumerate(range(int(a, 16), int(b, 16) + 1)):
                out[code] = chr(start + k)
    return out


def fonts_for(page: bytes, objs: dict[int, bytes]) -> dict[bytes, dict[int, str]]:
    res = page
    r = refs(page, b"Resources")
    if r:
        res = objs[r[0]]
    m = re.search(rb"/Font\s*(<<.*?>>|\d+ 0 R)", res, re.S)
    if not m:
        return {}
    fdict = m.group(1)
    if fdict.endswith(b"R"):
        fdict = objs[int(fdict.split()[0])]
    out = {}
    for name, num in re.findall(rb"/(\w+)\s+(\d+) 0 R", fdict):
        tu = refs(objs.get(int(num), b""), b"ToUnicode")
        out[name] = cmap(stream(objs[tu[0]])) if tu else {}
    return out


def decode(hexstr: bytes, table: dict) -> str:
    h = hexstr.decode()
    width = table.get("_w", 4)
    return "".join(table.get(int(h[i:i + width], 16), "") for i in range(0, len(h), width))


def page_texts(path: str) -> list[str]:
    data = open(path, "rb").read()
    objs = objects(data)
    catalog = next(b for b in objs.values() if b"/Type /Catalog" in b)
    order = []

    def walk(n):
        body = objs[n]
        if b"/Type /Pages" in body:
            for k in refs(body, b"Kids"):
                walk(k)
        else:
            order.append(n)

    walk(refs(catalog, b"Pages")[0])
    texts = []
    for n in order:
        page = objs[n]
        fonts = fonts_for(page, objs)
        content = b"".join(stream(objs[c]) for c in refs(page, b"Contents"))
        current, parts = {}, []
        for tok in re.finditer(rb"/(\w+)\s+[\d.]+\s+Tf|<([0-9A-Fa-f]+)>\s*Tj|\[(.*?)\]\s*TJ|(T\*|Td|TD|Tm)", content, re.S):
            if tok.group(1):
                current = fonts.get(tok.group(1), {})
            elif tok.group(2):
                parts.append(decode(tok.group(2), current))
            elif tok.group(3):
                parts.append("".join(decode(h, current) for h in re.findall(rb"<([0-9A-Fa-f]+)>", tok.group(3))))
            else:
                parts.append(" ")
        texts.append(re.sub(r"\s+", " ", "".join(parts)))
    return texts


if __name__ == "__main__":
    for i, t in enumerate(page_texts(sys.argv[1]), start=1):
        print(f"{i}\t{t}")
