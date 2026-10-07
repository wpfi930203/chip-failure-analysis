# -*- coding: utf-8 -*-
"""图标复核：左侧 2x 原图，右侧 32/40/64/100/200px 缩略条（棋盘底暴露透明区）。"""
import os
from PIL import Image

ICON = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "icons", "logo.png"))
OUT = r"D:\BaiduNetdiskDownload\失效分析\_tools\_icon_preview.png"

base = Image.open(ICON).convert("RGBA")
sizes = [32, 40, 64, 100, 200]
gap = 20
strip_w = sum(sizes) + gap * (len(sizes) + 1)
sheet = Image.new("RGB", (40 + 400 + 40 + strip_w, 460), (250, 250, 252))

big = base.resize((400, 400), Image.LANCZOS)
sheet.paste(big, (20, 30), big)

x = 20 + 400 + 40
for s in sizes:
    plate = Image.new("RGBA", (s, s), (255, 255, 255, 255))
    pd = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    pdd = ImageDraw.Draw(pd) if False else None
    for yy in range(0, s, 8):
        for xx in range(0, s, 8):
            col = (255, 255, 255, 255) if ((xx // 8) + (yy // 8)) % 2 == 0 else (205, 205, 212, 255)
            cell = Image.new("RGBA", (min(8, s - xx), min(8, s - yy)), col)
            plate.paste(cell, (xx, yy))
    y = 30 + (400 - s) // 2
    sheet.paste(plate, (x, y))
    sheet.paste(base.resize((s, s), Image.LANCZOS), (x, y), base.resize((s, s), Image.LANCZOS))
    x += s + gap

sheet.save(OUT)
print("PREVIEW:", OUT, sheet.size)
