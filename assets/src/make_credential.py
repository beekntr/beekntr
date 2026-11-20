#!/usr/bin/env python3
"""Regenerates assets/credential.svg, the animated hero card in the profile README.

Edit the text under "content", then run:
    pip install fonttools
    FONT_DIR=/path/to/fonts python3 make_credential.py ../credential.svg

FONT_DIR must contain these free Google Fonts (OFL), which get subset and embedded:
    crimsontext/CrimsonText-SemiBold.ttf
    firasans/FiraSans-Regular.ttf, FiraSans-Medium.ttf, FiraSans-ExtraBold.ttf
    anonymouspro/AnonymousPro-Regular.ttf
"""
import base64, io, math, os, sys
from fontTools import subset
from fontTools.ttLib import TTFont

OUT = sys.argv[1] if len(sys.argv) > 1 else "credential.svg"
FD = os.path.join(os.environ.get("FONT_DIR", "/usr/share/fonts/truetype/google-fonts/ofl"), "")

# ---------- tokens ----------
PAPER = "#E8EEF0"
PAPER_DEEP = "#DCE5E9"
INK = "#14253D"
MUTED = "#55657A"
TEAL = "#2F7F8F"
VIOLET = "#8A4F96"
STAMP = "#C23A2B"

W, H = 1200, 560
CX, CY = 60, 16            # card origin
CW, CH = 1080 + 80, 520    # card size (x 20..1180)
CARD_X, CARD_Y = 20, 16

# ---------- content ----------
NAME = "Kshitij Singh Bhati"
SUB = "Software developer at GullyCricket"
FIELDS = [
    ("Works on", "Wallets, payments, security"),
    ("Studying", "B.Tech CE, PIET Jaipur"),
    ("Runs", "A self-hosted home lab"),
    ("Building", "ZTA Firewall"),
]
CHECKS = ["Identity", "Device", "Context"]
HEADER_L = "Developer credential"
HEADER_R = "github.com/beekntr"
MICRO = "NEVERTRUSTALWAYSVERIFY"


def mrz(s, n=44):
    s = s.upper().replace(" ", "<")
    return (s + "<" * n)[:n]


MRZ1 = mrz("DEV<<BHATI<<KSHITIJ<SINGH")
MRZ2 = mrz("BEEKNTR<<NEVER<TRUST<<ALWAYS<VERIFY")
STAMP_RING = "NEVER TRUST  •  ALWAYS VERIFY  •  "
STAMP_WORD = "VERIFIED"
MONO = "KSB"


# ---------- font embedding ----------
def font_face(family, path, text, weight=400):
    opts = subset.Options()
    opts.flavor = "woff"
    opts.layout_features = ["kern", "liga"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    f = TTFont(path)
    s = subset.Subsetter(opts)
    s.populate(text="".join(sorted(set(text))) + " ")
    s.subset(f)
    buf = io.BytesIO()
    f.flavor = "woff"
    f.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};"
            f"src:url(data:font/woff;base64,{b64}) format('woff');}}")


all_fira_reg = HEADER_L + HEADER_R + "".join(l for l, _ in FIELDS) + "Policy check" + "".join(CHECKS) + MICRO
all_fira_med = SUB + "".join(v for _, v in FIELDS)
faces = "".join([
    font_face("CrimsonKSB", FD + "crimsontext/CrimsonText-SemiBold.ttf", NAME + MONO, 600),
    font_face("FiraKSB", FD + "firasans/FiraSans-Regular.ttf", all_fira_reg, 400),
    font_face("FiraKSB", FD + "firasans/FiraSans-Medium.ttf", all_fira_med, 500),
    font_face("FiraKSBX", FD + "firasans/FiraSans-ExtraBold.ttf", STAMP_RING + STAMP_WORD, 800),
    font_face("AnonKSB", FD + "anonymouspro/AnonymousPro-Regular.ttf", MRZ1 + MRZ2, 400),
])

SERIF = "'CrimsonKSB', 'Crimson Text', Georgia, 'Times New Roman', serif"
SANS = "'FiraKSB', 'Fira Sans', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
SANSX = "'FiraKSBX', 'Fira Sans', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONOF = "'AnonKSB', 'Anonymous Pro', ui-monospace, Menlo, Consolas, monospace"


# ---------- geometry helpers ----------
def fmt(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def polar_path(cx, cy, rfunc, steps):
    pts = []
    for k in range(steps + 1):
        t = 2 * math.pi * k / steps
        r = rfunc(t)
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    d = "M" + " L".join(f"{fmt(x)} {fmt(y)}" for x, y in pts) + "Z"
    return d


def param_path(fx, fy, t1, steps):
    pts = [(fx(t1 * k / steps), fy(t1 * k / steps)) for k in range(steps + 1)]
    return "M" + " L".join(f"{fmt(x)} {fmt(y)}" for x, y in pts) + "Z"


# ---------- rosette (guilloché seal) ----------
RX, RY = 222, 300
rosette = []   # (d, stroke-width, ring-index)

# outer woven ring: 6 interlaced 30-lobe waves
for i in range(6):
    ph = 2 * math.pi * i / (6 * 30) * 6 / 6
    rosette.append((polar_path(RX, RY, lambda t, ph=i * 2 * math.pi / 6: 150 + 7 * math.sin(30 * t + ph), 30 * 14), 0.9, 0))
# double rule
for r in (138, 134):
    rosette.append((polar_path(RX, RY, lambda t, r=r: r, 180), 0.8, 1))
# petal ring: 8 phase-shifted 12-lobe curves
for i in range(8):
    rosette.append((polar_path(RX, RY, lambda t, ph=i * 2 * math.pi / 8: 100 + 26 * math.sin(12 * t + ph), 12 * 18), 0.8, 2))
# inner spirograph (epitrochoid)
R_, r_, d_ = 42, 6, 22
k = (R_ + r_) / r_
rosette.append((param_path(lambda t: RX + (R_ + r_) * math.cos(t) - d_ * math.cos(k * t),
                           lambda t: RY + (R_ + r_) * math.sin(t) - d_ * math.sin(k * t),
                           2 * math.pi, 8 * 40), 0.8, 3))
for i in range(5):
    rosette.append((polar_path(RX, RY, lambda t, ph=i * 2 * math.pi / 5: 64 + 6 * math.sin(20 * t + ph), 20 * 12), 0.7, 3))

# ---------- background security pattern (tiled wave) ----------
tile_w, tile_h = 48, 7
wave = "M0 3.5 " + " ".join(
    f"L{fmt(x)} {fmt(3.5 + 2.2 * math.sin(2 * math.pi * x / tile_w))}" for x in range(1, tile_w + 1))

# broad guilloché band behind the lower half (few long curves)
band = []
for i in range(9):
    ph = i * math.pi / 9
    pts = []
    for xi in range(0, 1161, 6):
        x = CARD_X + xi
        y = 300 + 46 * math.sin(2 * math.pi * xi / 380 + ph) * math.sin(math.pi * xi / 1160 + 0.4) \
            + 14 * math.sin(2 * math.pi * xi / 95 + 2 * ph)
        pts.append(f"{fmt(x)} {fmt(y)}")
    band.append("M" + " L".join(pts))

# ---------- layout ----------
GX1, GX2 = 430, 800
NAME_Y = 182
SUB_Y = 222
ROW1_L, ROW1_V = 278, 306
ROW2_L, ROW2_V = 346, 374
CHK_L, CHK_Y = 414, 444
MRZ_Y1, MRZ_Y2 = 488, 518
SX, SY, SR = 1036, 398, 82

svg = []
a = svg.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
  f'aria-labelledby="t d">')
a('<title id="t">Kshitij Singh Bhati — developer credential</title>')
a('<desc id="d">A security-printed credential card. Kshitij Singh Bhati, software developer at GullyCricket. '
  'Works on wallets, payments and security; studying B.Tech Computer Engineering at PIET Jaipur; runs a self-hosted '
  'home lab; building ZTA Firewall. Policy check: identity, device and context verified. Stamped verified.</desc>')

css = f"""
{faces}
.serif{{font-family:{SERIF};font-weight:600}}
.sans{{font-family:{SANS};font-weight:400}}
.med{{font-family:{SANS};font-weight:500}}
.mono{{font-family:{MONOF}}}
.stampf{{font-family:{SANSX};font-weight:800}}
.draw{{stroke-dasharray:1;stroke-dashoffset:0;animation:draw 1.6s cubic-bezier(.55,.1,.25,1) both}}
.fade{{animation:fade .7s ease-out both}}
.tick{{stroke-dasharray:1;stroke-dashoffset:0;animation:draw .35s ease-out both}}
.ring{{animation:fade .25s ease-out both}}
.stamp{{transform-origin:0 0;animation:stamp .42s cubic-bezier(.2,1.4,.4,1) both;animation-delay:3.05s}}
@keyframes draw{{from{{stroke-dashoffset:1}}to{{stroke-dashoffset:0}}}}
@keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes stamp{{0%{{opacity:0;transform:scale(1.7)}}60%{{opacity:.92}}100%{{opacity:.9;transform:scale(1)}}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
"""
a(f"<style>{css}</style>")

a("<defs>")
a(f'<linearGradient id="iris" gradientUnits="userSpaceOnUse" x1="{RX-150}" y1="{RY-150}" x2="{RX+150}" y2="{RY+150}">'
  f'<stop offset="0" stop-color="{TEAL}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>')
a(f'<linearGradient id="iris2" gradientUnits="userSpaceOnUse" x1="{CARD_X}" y1="0" x2="{CARD_X+CW}" y2="0">'
  f'<stop offset="0" stop-color="{TEAL}"/><stop offset=".55" stop-color="{VIOLET}"/><stop offset="1" stop-color="{TEAL}"/></linearGradient>')
a(f'<pattern id="paper" width="{tile_w}" height="{tile_h}" patternUnits="userSpaceOnUse">'
  f'<path d="{wave}" fill="none" stroke="{TEAL}" stroke-width=".55" opacity=".22"/></pattern>')
a('<linearGradient id="bandfade" x1="0" y1="0" x2="1" y2="0">'
  '<stop offset="0" stop-color="#fff"/><stop offset=".3" stop-color="#fff"/>'
  '<stop offset=".39" stop-color="#fff" stop-opacity=".22"/><stop offset=".82" stop-color="#fff" stop-opacity=".22"/>'
  '<stop offset=".93" stop-color="#fff"/><stop offset="1" stop-color="#fff"/></linearGradient>')
a(f'<mask id="bandmask"><rect x="{CARD_X}" y="{CARD_Y}" width="{CW}" height="{CH}" fill="url(#bandfade)"/></mask>')
a(f'<clipPath id="card"><rect x="{CARD_X}" y="{CARD_Y}" width="{CW}" height="{CH}" rx="26"/></clipPath>')
a('<filter id="shadow" x="-5%" y="-5%" width="110%" height="120%">'
  '<feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#0B1220" flood-opacity=".28"/></filter>')
# ink-distress for the rubber stamp
a('<filter id="ink" x="-20%" y="-20%" width="140%" height="140%">'
  '<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="7" result="n"/>'
  '<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -4.2 3.05" result="m"/>'
  '<feComposite in="SourceGraphic" in2="m" operator="in"/></filter>')
c25, s25 = math.cos(math.radians(25)), math.sin(math.radians(25))
a(f'<path id="arcTop" d="M {fmt(-67*c25)} {fmt(-67*s25)} A 67 67 0 0 1 {fmt(67*c25)} {fmt(-67*s25)}"/>')
a(f'<path id="arcBot" d="M {fmt(-77*c25)} {fmt(77*s25)} A 77 77 0 0 0 {fmt(77*c25)} {fmt(77*s25)}"/>')
a("</defs>")

# card
a(f'<rect x="{CARD_X}" y="{CARD_Y}" width="{CW}" height="{CH}" rx="26" fill="{PAPER}" filter="url(#shadow)"/>')
a('<g clip-path="url(#card)">')
a(f'<rect x="{CARD_X}" y="{CARD_Y}" width="{CW}" height="{CH}" fill="url(#paper)"/>')
a(f'<g class="fade" style="animation-duration:1.2s" fill="none" stroke="url(#iris2)" stroke-width=".7" opacity=".38" mask="url(#bandmask)">')
for d in band:
    a(f'<path d="{d}"/>')
a("</g>")
# MRZ zone
a(f'<rect x="{CARD_X}" y="{MRZ_Y1-34}" width="{CW}" height="{CH-(MRZ_Y1-34-CARD_Y)}" fill="{PAPER}"/>')
a(f'<rect x="{CARD_X}" y="{MRZ_Y1-34}" width="{CW}" height="{CH-(MRZ_Y1-34-CARD_Y)}" fill="{PAPER_DEEP}" opacity=".55"/>')
a("</g>")
a(f'<rect x="{CARD_X+.5}" y="{CARD_Y+.5}" width="{CW-1}" height="{CH-1}" rx="25.5" fill="none" stroke="{INK}" stroke-opacity=".12"/>')

# header + microtext rule
a(f'<text class="sans" x="60" y="66" font-size="18" fill="{MUTED}" letter-spacing=".4">{HEADER_L}</text>')
a(f'<text class="sans" x="1140" y="66" font-size="18" fill="{MUTED}" text-anchor="end" letter-spacing=".4">{HEADER_R}</text>')
micro = (MICRO * 40)[:330]
a(f'<text class="sans" x="60" y="88" font-size="5.6" fill="{INK}" opacity=".55" textLength="1080" lengthAdjust="spacingAndGlyphs">{micro}</text>')

# rosette
a(f'<g fill="none" stroke="url(#iris)">')
for idx, (d, sw, ring) in enumerate(rosette):
    delay = 0.05 + ring * 0.22 + (idx % 8) * 0.03
    a(f'<path class="draw" pathLength="1" style="animation-delay:{delay:.2f}s" stroke-width="{sw}" d="{d}"/>')
a("</g>")
a(f'<g class="fade" style="animation-delay:1.1s">')
a(f'<circle cx="{RX}" cy="{RY}" r="38" fill="{PAPER}" stroke="{INK}" stroke-width="1.2"/>')
a(f'<circle cx="{RX}" cy="{RY}" r="33" fill="none" stroke="{INK}" stroke-width=".6" stroke-opacity=".6"/>')
a(f'<text class="serif" x="{RX}" y="{RY+10}" font-size="28" fill="{INK}" text-anchor="middle" letter-spacing="1.5">{MONO}</text>')
a("</g>")

# name + subtitle
a(f'<g class="fade" style="animation-delay:.35s">')
a(f'<text class="serif" x="{GX1}" y="{NAME_Y}" font-size="66" fill="{INK}" letter-spacing="-.4">{NAME}</text>')
a(f'<text class="med" x="{GX1+2}" y="{SUB_Y}" font-size="25" fill="{INK}" opacity=".88">{SUB}</text>')
a("</g>")

# fields
pos = [(GX1, ROW1_L, ROW1_V), (GX2, ROW1_L, ROW1_V), (GX1, ROW2_L, ROW2_V), (GX2, ROW2_L, ROW2_V)]
for n, ((lab, val), (x, yl, yv)) in enumerate(zip(FIELDS, pos)):
    a(f'<g class="fade" style="animation-delay:{0.6 + n*0.12:.2f}s">')
    a(f'<text class="sans" x="{x+2}" y="{yl}" font-size="16" fill="{MUTED}">{lab}</text>')
    a(f'<text class="med" x="{x+2}" y="{yv}" font-size="22" fill="{INK}">{val}</text>')
    a("</g>")

# policy check
a(f'<text class="sans fade" style="animation-delay:1.3s" x="{GX1+2}" y="{CHK_L}" font-size="16" fill="{MUTED}">Policy check</text>')
cx = GX1 + 14
for n, lab in enumerate(CHECKS):
    t0 = 1.75 + n * 0.38
    a(f'<g>')
    a(f'<circle class="ring" style="animation-delay:{t0:.2f}s" cx="{cx}" cy="{CHK_Y-7}" r="11.5" fill="{TEAL}" fill-opacity=".14" stroke="{TEAL}" stroke-width="1.6"/>')
    a(f'<path class="tick" style="animation-delay:{t0+0.12:.2f}s" pathLength="1" d="M{cx-5.5} {CHK_Y-7} l3.8 4 l7.4 -8" fill="none" stroke="{TEAL}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
    a(f'<text class="med fade" style="animation-delay:{t0:.2f}s" x="{cx+20}" y="{CHK_Y}" font-size="20" fill="{INK}">{lab}</text>')
    a("</g>")
    cx += 128

# MRZ
a(f'<g class="mono fade" style="animation-delay:.9s" font-size="25" fill="{INK}">')
a(f'<text x="60" y="{MRZ_Y1}" textLength="1080" lengthAdjust="spacing">{MRZ1.replace("<", "&lt;")}</text>')
a(f'<text x="60" y="{MRZ_Y2}" textLength="1080" lengthAdjust="spacing">{MRZ2.replace("<", "&lt;")}</text>')
a("</g>")

# stamp
a(f'<g transform="translate({SX} {SY}) rotate(-13)" style="mix-blend-mode:multiply">')
a(f'<g class="stamp" filter="url(#ink)" fill="{STAMP}" stroke="{STAMP}">')
a(f'<circle r="{SR}" fill="none" stroke-width="5"/>')
a(f'<circle r="{SR-21}" fill="none" stroke-width="2"/>')
a('<text class="stampf" font-size="14" stroke="none" letter-spacing="2.2" text-anchor="middle">'
  '<textPath href="#arcTop" startOffset="50%">NEVER TRUST</textPath></text>')
a('<text class="stampf" font-size="14" stroke="none" letter-spacing="2.2" text-anchor="middle">'
  '<textPath href="#arcBot" startOffset="50%">ALWAYS VERIFY</textPath></text>')
a('<circle cx="-72" cy="0" r="2.6" stroke="none"/><circle cx="72" cy="0" r="2.6" stroke="none"/>')
a(f'<rect x="-98" y="-21" width="196" height="42" rx="3" fill="{PAPER}" stroke="none"/>')
a(f'<rect x="-98" y="-21" width="196" height="42" rx="3" fill="none" stroke-width="3.5"/>')
a(f'<text class="stampf" x="0" y="11" font-size="31" text-anchor="middle" stroke="none" letter-spacing="3" '
  f'textLength="170" lengthAdjust="spacingAndGlyphs">{STAMP_WORD}</text>')
a("</g></g>")

a("</svg>")

with open(OUT, "w") as f:
    f.write("\n".join(svg))
print(OUT, sum(len(s) for s in svg) // 1024, "KB")
