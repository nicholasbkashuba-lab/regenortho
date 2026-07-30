"""The homepage figure — a luminous human form, not an anatomy chart.

RegenOrtho sits between orthopedics and a med spa. A skeleton reads as the
former only: correct, clinical, and cold beside an IV lounge and a peptide menu.
This figure keeps the same interactive treatment-area navigation but renders the
body as soft light — closer to a wellness ritual menu than a diagram.

Geometry still derives from the LANDMARKS in figure.py so the hotspots, the
label leaders and the form stay locked together.
"""
from figure import (VB_W, VB_H, CX, CROWN, CHIN, NECK_BOT, SHOULDER_Y, SHOULDER_DX,
                    ELBOW_Y, ELBOW_DX, WRIST_Y, WRIST_DX, RIB_TOP, RIB_BOT,
                    PELVIS_TOP, HIP_Y, HIP_DX, KNEE_Y, KNEE_DX, ANKLE_Y, ANKLE_DX,
                    FOOT_BOT, _f)

WAIST_Y, WAIST_DX = RIB_BOT + 18, 34
HIPS_DX = 46
CHEST_DX = 50


def _form():
    """Head, trunk, limbs as separate soft masses. A single closed silhouette
    needs armpit and crotch notches that fight the blur; separate masses read as
    one body once the glow unifies them, and each can breathe independently."""
    p = []

    # head
    p.append(f'<ellipse class="au-mass" cx="{CX}" cy="{_f((CROWN + CHIN) / 2)}" '
             f'rx="25" ry="{_f((CHIN - CROWN) / 2)}"/>')

    # neck into shoulders, chest, waist, hips — one flowing trunk
    p.append(
        '<path class="au-mass" d="'
        f'M{CX - 11},{_f(CHIN - 4)} '
        f'C{CX - 13},{_f(NECK_BOT)} {_f(CX - CHEST_DX)},{_f(SHOULDER_Y - 4)} '
        f'{_f(CX - CHEST_DX)},{_f(RIB_TOP + 40)} '
        f'C{_f(CX - CHEST_DX + 4)},{_f(RIB_BOT - 10)} {_f(CX - WAIST_DX)},{_f(WAIST_Y - 10)} '
        f'{_f(CX - WAIST_DX)},{_f(WAIST_Y)} '
        f'C{_f(CX - WAIST_DX - 4)},{_f(PELVIS_TOP + 10)} {_f(CX - HIPS_DX)},{_f(HIP_Y - 20)} '
        f'{_f(CX - HIPS_DX)},{_f(HIP_Y + 6)} '
        f'C{_f(CX - HIPS_DX)},{_f(HIP_Y + 34)} {CX - 30},{_f(HIP_Y + 46)} {CX},{_f(HIP_Y + 48)} '
        f'C{CX + 30},{_f(HIP_Y + 46)} {_f(CX + HIPS_DX)},{_f(HIP_Y + 34)} '
        f'{_f(CX + HIPS_DX)},{_f(HIP_Y + 6)} '
        f'C{_f(CX + HIPS_DX)},{_f(HIP_Y - 20)} {_f(CX + WAIST_DX + 4)},{_f(PELVIS_TOP + 10)} '
        f'{_f(CX + WAIST_DX)},{_f(WAIST_Y)} '
        f'C{_f(CX + WAIST_DX)},{_f(WAIST_Y - 10)} {_f(CX + CHEST_DX - 4)},{_f(RIB_BOT - 10)} '
        f'{_f(CX + CHEST_DX)},{_f(RIB_TOP + 40)} '
        f'C{_f(CX + CHEST_DX)},{_f(SHOULDER_Y - 4)} {CX + 13},{_f(NECK_BOT)} '
        f'{CX + 11},{_f(CHIN - 4)}Z"/>'
    )

    for s in (-1, 1):
        sx, ex, wx = CX + s * SHOULDER_DX, CX + s * ELBOW_DX, CX + s * WRIST_DX
        hx, kx, ax = CX + s * HIP_DX, CX + s * KNEE_DX, CX + s * ANKLE_DX
        # arm, tapering wrist-ward
        p.append(
            '<path class="au-mass" d="'
            f'M{_f(sx - s * 12)},{_f(SHOULDER_Y - 2)} '
            f'C{_f(sx + s * 6)},{_f(SHOULDER_Y + 20)} {_f(ex + s * 6)},{_f(ELBOW_Y - 40)} '
            f'{_f(ex + s * 4)},{_f(ELBOW_Y)} '
            f'C{_f(ex + s * 6)},{_f(ELBOW_Y + 44)} {_f(wx + s * 5)},{_f(WRIST_Y - 40)} '
            f'{_f(wx + s * 2)},{_f(WRIST_Y + 26)} '
            f'C{_f(wx - s * 10)},{_f(WRIST_Y + 28)} {_f(wx - s * 12)},{_f(WRIST_Y - 30)} '
            f'{_f(ex - s * 24)},{_f(ELBOW_Y - 4)} '
            f'C{_f(ex - s * 26)},{_f(ELBOW_Y - 48)} {_f(sx - s * 34)},{_f(SHOULDER_Y + 26)} '
            f'{_f(sx - s * 12)},{_f(SHOULDER_Y - 2)}Z"/>'
        )
        # leg, thigh through calf to ankle
        p.append(
            '<path class="au-mass" d="'
            f'M{_f(hx - s * 22)},{_f(HIP_Y + 6)} '
            f'C{_f(hx + s * 17)},{_f(HIP_Y + 16)} {_f(kx + s * 15)},{_f(KNEE_Y - 90)} '
            f'{_f(kx + s * 11)},{_f(KNEE_Y)} '
            f'C{_f(kx + s * 15)},{_f(KNEE_Y + 70)} {_f(ax + s * 10)},{_f(ANKLE_Y - 90)} '
            f'{_f(ax + s * 9)},{_f(ANKLE_Y + 8)} '
            f'L{_f(ax - s * 9)},{_f(ANKLE_Y + 8)} '
            f'C{_f(ax - s * 12)},{_f(ANKLE_Y - 90)} {_f(kx - s * 16)},{_f(KNEE_Y + 66)} '
            f'{_f(kx - s * 13)},{_f(KNEE_Y)} '
            f'C{_f(kx - s * 16)},{_f(KNEE_Y - 86)} {_f(hx - s * 21)},{_f(HIP_Y + 40)} '
            f'{_f(hx - s * 22)},{_f(HIP_Y + 6)}Z"/>'
        )
    return p


def _threads(nodes):
    """Slow light running between the treatment points — the visual claim that
    the practice treats a connected system, not eight separate complaints."""
    out = []
    pts = [(x, y) for _k, x, y, *_r in nodes]
    pts.sort(key=lambda q: q[1])
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        bow = 26 if i % 2 == 0 else -26
        out.append(f'<path class="au-thread" style="--td:{i * 0.7}s" '
                   f'd="M{_f(x1)},{_f(y1)} Q{_f(mx + bow)},{_f(my)} {_f(x2)},{_f(y2)}"/>')
    return out


def _motes():
    """Drifting particles. Deterministic positions — no RNG, so a rebuild never
    reshuffles the composition."""
    out = []
    seeds = [(0.18, 0.22), (0.82, 0.16), (0.10, 0.55), (0.90, 0.48), (0.26, 0.83),
             (0.74, 0.76), (0.50, 0.08), (0.06, 0.34), (0.94, 0.66), (0.40, 0.94)]
    for i, (fx, fy) in enumerate(seeds):
        out.append(f'<circle class="au-mote" style="--md:{i * 1.3}s" '
                   f'cx="{_f(fx * VB_W)}" cy="{_f(fy * VB_H)}" r="{2.4 if i % 3 else 3.4}"/>')
    return out


def aura_svg(nodes):
    return "\n      ".join(_form() + _threads(nodes) + _motes())


def aura_defs():
    # userSpaceOnUse is load-bearing: the default objectBoundingBox maps a fresh
    # gradient onto EVERY shape, so head, torso and each limb were lit separately
    # and the body broke into visibly seamed parts.
    return f"""<radialGradient id="auBody" gradientUnits="userSpaceOnUse" \
        cx="{_f(CX - 40)}" cy="{_f(VB_H * 0.3)}" r="{_f(VB_H * 0.72)}">
        <stop offset="0" stop-color="#FFF0C4" stop-opacity=".72"/>
        <stop offset=".4" stop-color="#EFBB58" stop-opacity=".4"/>
        <stop offset=".74" stop-color="#9C6EC4" stop-opacity=".26"/>
        <stop offset="1" stop-color="#4E62C6" stop-opacity=".1"/>
      </radialGradient>
      <radialGradient id="auHalo" cx=".5" cy=".42" r=".6">
        <stop offset="0" stop-color="#FDC929" stop-opacity=".2"/>
        <stop offset=".5" stop-color="#3E6FB4" stop-opacity=".13"/>
        <stop offset="1" stop-color="#12457F" stop-opacity="0"/>
      </radialGradient>
      <filter id="auSoft" x="-30%" y="-30%" width="160%" height="160%">
        <feGaussianBlur stdDeviation="4.6"/>
      </filter>
      <filter id="auBloom" x="-40%" y="-40%" width="180%" height="180%">
        <feGaussianBlur stdDeviation="13" result="b"/>
        <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>"""
