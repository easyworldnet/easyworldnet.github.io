"""Builds the two A4 QR posters from poster.html and ../qr.svg.

Run from anywhere:  python3 stampa/genera.py
Output: stampa/qr-a4-fiori.pdf and stampa/qr-a4-semplice.pdf

New address?  python3 stampa/genera.py --url https://...
first rewrites ../qr.svg and ../qr.png for that address, then builds the posters.
"""
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
QUIET = 4  # white border, in modules, that scanners need around the code


def make_qr(url):
    rows = subprocess.run(["swift", str(HERE / "qr.swift"), url],
                          check=True, capture_output=True, text=True).stdout.split()
    size = len(rows) + 2 * QUIET
    squares = "".join(
        f"M{x + QUIET},{y + QUIET}H{x + QUIET + 1}V{y + QUIET + 1}H{x + QUIET}z"
        for y, row in enumerate(rows) for x, bit in enumerate(row) if bit == "1"
    )
    svg = HERE.parent / "qr.svg"
    svg.write_text(
        "<?xml version='1.0' encoding='UTF-8'?>\n"
        f'<svg width="{size}mm" height="{size}mm" version="1.1" viewBox="0 0 {size} {size}" '
        f'xmlns="http://www.w3.org/2000/svg"><rect width="{size}" height="{size}" fill="#fff"/>'
        f'<path d="{squares}" fill="#000"/></svg>\n'
    )
    subprocess.run(["magick", "-density", "1200", str(svg), "-resize", f"{size * 20}x{size * 20}",
                    "-threshold", "50%", "-type", "bilevel", str(HERE.parent / "qr.png")], check=True)
    print("ok qr.svg + qr.png", f"({len(rows)}x{len(rows)} modules)")


def qr_path():
    # qr.svg draws one 1x1 square per dark module. Merge each row into runs so
    # PDF viewers don't show hairline seams between neighbouring squares.
    svg = (HERE.parent / "qr.svg").read_text()
    size = int(re.search(r'viewBox="0 0 (\d+)', svg).group(1))
    cells = {(int(x), int(y)) for x, y in re.findall(r"M(\d+),(\d+)H", svg)}
    parts = []
    for y in sorted({y for _, y in cells}):
        xs = sorted(x for x, yy in cells if yy == y)
        start = prev = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == prev + 1:
                prev = x
                continue
            # 1.02 tall: rows overlap slightly, so no seams vertically either.
            parts.append(f"M{start},{y}h{prev - start + 1}v1.02h-{prev - start + 1}z")
            if x is not None:
                start = prev = x
    return size, "".join(parts)


def main():
    if "--url" in sys.argv:
        make_qr(sys.argv[sys.argv.index("--url") + 1])
    size, path = qr_path()
    html = (HERE / "poster.html").read_text()
    page = HERE / "_poster-build.html"
    page.write_text(html.replace("{{QR_PATH}}", path).replace("{{QR_SIZE}}", str(size)))
    for name, query in (("qr-a4-fiori.pdf", ""), ("qr-a4-semplice.pdf", "?semplice")):
        subprocess.run([
            CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
            "--virtual-time-budget=8000", f"--print-to-pdf={HERE / name}",
            page.as_uri() + query,
        ], check=True, capture_output=True)
        print("ok", name)
    page.unlink()


if __name__ == "__main__":
    main()
