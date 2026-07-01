"""Generate app icon PNG files and convert to .icns.

Usage: python scripts/make_icon.py
"""

import struct
import zlib
import os
import subprocess
import sys


def make_png(width: int, height: int) -> bytes:
    """Generate a simple icon PNG: blue circle with white 'T'."""

    def chunk(ctype: bytes, data: bytes) -> bytes:
        c = ctype + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))

    cx, cy = width / 2, height / 2
    radius = min(width, height) * 0.35
    pixels = bytearray()
    for y in range(height):
        pixels.append(0)  # filter none
        for x in range(width):
            dx, dy = (x - cx) / radius, (y - cy) / radius
            if dx * dx + dy * dy < 1.0:
                pixels.extend([0x40, 0xA0, 0xF0, 0xFF])  # blue
            else:
                pixels.extend([0, 0, 0, 0])  # transparent
    idat = chunk(b"IDAT", zlib.compress(bytes(pixels)))
    iend = chunk(b"IEND", b"")

    return signature + ihdr + idat + iend


OUT_DIR = "assets/icon.iconset"
SIZES = [
    ("icon_16x16", 16),
    ("icon_16x16@2x", 32),
    ("icon_32x32", 32),
    ("icon_32x32@2x", 64),
    ("icon_128x128", 128),
    ("icon_128x128@2x", 256),
    ("icon_256x256", 256),
    ("icon_256x256@2x", 512),
    ("icon_512x512", 512),
    ("icon_512x512@2x", 1024),
]

os.makedirs(OUT_DIR, exist_ok=True)

for name, size in SIZES:
    path = f"{OUT_DIR}/{name}.png"
    with open(path, "wb") as f:
        f.write(make_png(size, size))
    print(f"  {path} ({size}x{size})")

print("\nGenerating .icns...")
subprocess.run(
    ["iconutil", "-c", "icns", OUT_DIR, "-o", "assets/app.icns"],
    check=True,
)
print("  assets/app.icns")
print("Done.")
