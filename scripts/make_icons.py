#!/usr/bin/env python3
"""Generate simple solid-color PWA icons as valid PNGs using only the stdlib.

Produces a navy square with a lighter rounded inner square — enough for a clean,
recognizable home-screen icon without pulling in an image library.
"""
import struct
import zlib
from pathlib import Path

NAVY = (31, 59, 87)       # #1f3b57
ACCENT = (255, 216, 20)   # #ffd814


def _chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def write_png(path: Path, size: int) -> None:
    # Build RGBA pixel rows.
    rows = bytearray()
    pad = size // 6              # margin for the inner square
    inner0, inner1 = pad, size - pad
    radius = size // 8           # rough rounded-corner inset for inner square

    for y in range(size):
        rows.append(0)  # PNG filter byte (none) at the start of each row
        for x in range(size):
            # Default background: navy.
            r, g, b = NAVY
            # Inner accent square (with crude rounded corners).
            if inner0 <= x < inner1 and inner0 <= y < inner1:
                cx = x - inner0
                cy = y - inner0
                w = inner1 - inner0
                in_corner = (
                    (cx < radius and cy < radius and (radius - cx) ** 2 + (radius - cy) ** 2 > radius ** 2)
                    or (cx > w - radius and cy < radius and (cx - (w - radius)) ** 2 + (radius - cy) ** 2 > radius ** 2)
                    or (cx < radius and cy > w - radius and (radius - cx) ** 2 + (cy - (w - radius)) ** 2 > radius ** 2)
                    or (cx > w - radius and cy > w - radius and (cx - (w - radius)) ** 2 + (cy - (w - radius)) ** 2 > radius ** 2)
                )
                if not in_corner:
                    r, g, b = ACCENT
            rows += bytes((r, g, b, 255))

    raw = zlib.compress(bytes(rows), 9)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    png += _chunk(b"IDAT", raw)
    png += _chunk(b"IEND", b"")
    path.write_bytes(png)
    print(f"wrote {path} ({size}x{size}, {len(png)} bytes)")


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    out = project_root / "app" / "static" / "icons"
    out.mkdir(parents=True, exist_ok=True)
    write_png(out / "icon-192.png", 192)
    write_png(out / "icon-512.png", 512)


if __name__ == "__main__":
    main()
