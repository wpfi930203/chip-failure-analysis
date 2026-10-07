# -*- coding: utf-8 -*-
"""生成「芯片失效分析」skill 图标：芯片 + 裂纹（裂纹源标记）。

纯 Pillow 手绘矢量，不调用任何图像生成 API。
输出：icons/logo.png（200x200，4x 超采样 + LANCZOS 降采样）
      icons/logo.svg（与 PNG 结构一致的矢量源）

设计语义（详见 icons/README.md）：
  方形封装体 + 四面引脚 = 芯片（无歧义的领域符号）
  封装体上的裂纹 + 裂纹源实心点 = 失效分析（把"坏了"编码进图形）
"""
import os
from PIL import Image, ImageDraw

# ---------------------------------------------------------------- 画布
W = 200          # 逻辑尺寸
S = 4            # 超采样倍数
C = W * S        # 实际绘制尺寸 800

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icons")
OUT_DIR = os.path.normpath(OUT_DIR)

# ---------------------------------------------------------------- 配色
BG_TOP  = (14, 58, 68)      # #0E3A44  深青蓝（底色上浅色才够亮）
BG_BOT  = (6, 34, 43)       # #06222B
PIN     = (168, 223, 233)   # #A8DFE9  引脚
BODY_F  = (234, 247, 250)   # #EAF7FA  封装体
BODY_L  = (134, 207, 222)   # #86CFDE  封装体描边
DIE_TOP = (18, 82, 95)      # #12525F  芯片裸片（深色，与封装体拉开层次）
DIE_BOT = (10, 54, 65)      # #0A3641
DIE_L   = (111, 198, 214)   # #6FC6D6  裸片描边
CRACK   = (255, 122, 69)    # #FF7A45  裂纹（与青底成互补色，32px 下仍可辨）
HOT     = (255, 210, 184)   # #FFD2B8  裂纹源高光

# ---------------------------------------------------------------- 几何（200 逻辑坐标）
PIN_L, PIN_W, PIN_R = 18, 10, 3
BODY0, BODY1, BODY_R = 50, 150, 12
DIE0, DIE1, DIE_R = 70, 130, 6
BG_R = 44
PIN_CENTERS = [62.0, 87.3333, 112.6667, 138.0]
CRACK_PATH = [(130, 72), (123, 79), (110, 90), (118, 100), (100, 112), (106, 120), (80, 130)]
ORIGIN = (123, 79)


def lerp(c0, c1, t):
    return tuple(int(round(c0[i] + (c1[i] - c0[i]) * t)) for i in range(3))


def gradient(size, c0, c1, diagonal=True, n=128):
    """低分辨率逐像素算渐变再放大，避免逐像素遍历 800x800。"""
    g = Image.new("RGB", (n, n))
    px = g.load()
    for y in range(n):
        for x in range(n):
            t = ((x + y) / (2.0 * (n - 1))) if diagonal else (y / (n - 1.0))
            px[x, y] = lerp(c0, c1, t)
    return g.resize((size, size), Image.BICUBIC)


def rounded_mask(size, radius):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return m


def draw():
    img = Image.new("RGB", (C, C), BG_BOT)
    img.paste(gradient(C, BG_TOP, BG_BOT, diagonal=True), (0, 0), rounded_mask(C, BG_R * S))
    d = ImageDraw.Draw(img)

    # 1) 四面引脚（先画，让封装体压住根部）
    for cy in PIN_CENTERS:
        y0, y1 = (cy - PIN_W / 2) * S, (cy + PIN_W / 2) * S
        d.rounded_rectangle([(BODY0 - PIN_L) * S, y0, BODY0 * S, y1], radius=PIN_R * S, fill=PIN)
        d.rounded_rectangle([BODY1 * S, y0, (BODY1 + PIN_L) * S, y1], radius=PIN_R * S, fill=PIN)
    for cx in PIN_CENTERS:
        x0, x1 = (cx - PIN_W / 2) * S, (cx + PIN_W / 2) * S
        d.rounded_rectangle([x0, (BODY0 - PIN_L) * S, x1, BODY0 * S], radius=PIN_R * S, fill=PIN)
        d.rounded_rectangle([x0, BODY1 * S, x1, (BODY1 + PIN_L) * S], radius=PIN_R * S, fill=PIN)

    # 2) 封装体
    d.rounded_rectangle([BODY0 * S, BODY0 * S, BODY1 * S, BODY1 * S],
                        radius=BODY_R * S, fill=BODY_F, outline=BODY_L, width=3 * S)

    # 3) 芯片裸片（深色，与浅色封装体形成内/外层次）
    die = gradient(C, DIE_TOP, DIE_BOT, diagonal=False)
    die_mask = Image.new("L", (C, C), 0)
    ImageDraw.Draw(die_mask).rounded_rectangle(
        [DIE0 * S, DIE0 * S, DIE1 * S, DIE1 * S], radius=DIE_R * S, fill=255)
    img.paste(die, (0, 0), die_mask)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([DIE0 * S, DIE0 * S, DIE1 * S, DIE1 * S],
                        radius=DIE_R * S, outline=DIE_L, width=int(round(2.5 * S)))

    # 4) 裂纹：粗线 + 顶点圆角（模拟圆头线帽）
    pts = [(int(round(x * S)), int(round(y * S))) for x, y in CRACK_PATH]
    cw = int(round(6 * S))
    d.line(pts, fill=CRACK, width=cw, joint="curve")
    r = cw / 2.0
    for (x, y) in pts:
        d.ellipse([x - r, y - r, x + r, y + r], fill=CRACK)

    # 5) 裂纹源标记（实心点 + 高光芯）——"定位到起点"是失效分析的第一动作
    ox, oy = ORIGIN[0] * S, ORIGIN[1] * S
    d.ellipse([ox - 9.5 * S, oy - 9.5 * S, ox + 9.5 * S, oy + 9.5 * S], fill=CRACK)
    d.ellipse([ox - 3.2 * S, oy - 3.2 * S, ox + 3.2 * S, oy + 3.2 * S], fill=HOT)

    return img.resize((W, W), Image.LANCZOS)


SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
  <!-- 芯片失效分析 · chip + crack（裂纹源自封装体边缘起始，贯穿裸片）-->
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0E3A44"/>
      <stop offset="1" stop-color="#06222B"/>
    </linearGradient>
    <linearGradient id="die" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#12525F"/>
      <stop offset="1" stop-color="#0A3641"/>
    </linearGradient>
  </defs>
  <rect width="200" height="200" rx="44" fill="url(#bg)"/>
  <!-- 四面引脚 -->
  <g fill="#A8DFE9">
    <rect x="32" y="57" width="18" height="10" rx="3"/>
    <rect x="32" y="82.33" width="18" height="10" rx="3"/>
    <rect x="32" y="107.67" width="18" height="10" rx="3"/>
    <rect x="32" y="133" width="18" height="10" rx="3"/>
    <rect x="150" y="57" width="18" height="10" rx="3"/>
    <rect x="150" y="82.33" width="18" height="10" rx="3"/>
    <rect x="150" y="107.67" width="18" height="10" rx="3"/>
    <rect x="150" y="133" width="18" height="10" rx="3"/>
    <rect x="57" y="32" width="10" height="18" rx="3"/>
    <rect x="82.33" y="32" width="10" height="18" rx="3"/>
    <rect x="107.67" y="32" width="10" height="18" rx="3"/>
    <rect x="133" y="32" width="10" height="18" rx="3"/>
    <rect x="57" y="150" width="10" height="18" rx="3"/>
    <rect x="82.33" y="150" width="10" height="18" rx="3"/>
    <rect x="107.67" y="150" width="10" height="18" rx="3"/>
    <rect x="133" y="150" width="10" height="18" rx="3"/>
  </g>
  <!-- 封装体 -->
  <rect x="50" y="50" width="100" height="100" rx="12" fill="#EAF7FA" stroke="#86CFDE" stroke-width="3"/>
  <!-- 芯片裸片 -->
  <rect x="70" y="70" width="60" height="60" rx="6" fill="url(#die)" stroke="#6FC6D6" stroke-width="2.5"/>
  <!-- 裂纹（自右上角边缘起始，贯穿至左下边缘；折线为"脆性断裂"而非塑性变形）-->
  <polyline points="130,72 123,79 110,90 118,100 100,112 106,120 80,130"
            fill="none" stroke="#FF7A45" stroke-width="6"
            stroke-linecap="round" stroke-linejoin="round"/>
  <!-- 裂纹源标记 -->
  <circle cx="123" cy="79" r="9.5" fill="#FF7A45"/>
  <circle cx="123" cy="79" r="3.2" fill="#FFD2B8"/>
</svg>
"""


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    png_path = os.path.join(OUT_DIR, "logo.png")
    svg_path = os.path.join(OUT_DIR, "logo.svg")
    draw().save(png_path, "PNG", optimize=True)
    with open(svg_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(SVG)
    print("PNG:", png_path, os.path.getsize(png_path), "bytes")
    print("SVG:", svg_path, os.path.getsize(svg_path), "bytes")


if __name__ == "__main__":
    main()
