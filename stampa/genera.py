"""Builds the two A4 QR posters from poster.html and ../qr.svg.

Run from anywhere:  python3 stampa/genera.py
Output: stampa/qr-a4-fiori.pdf and stampa/qr-a4-semplice.pdf
"""
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def qr_path():
    # qr.svg draws one 1x1 square per dark module. Merge each row into runs so
    # PDF viewers don't show hairline seams between neighbouring squares.
    svg = (HERE.parent / "qr.svg").read_text()
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
    return "".join(parts)


def main():
    page = HERE / "_poster-build.html"
    page.write_text((HERE / "poster.html").read_text().replace("{{QR_PATH}}", qr_path()))
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
