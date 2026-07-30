"""The interactive anatomy figure — a drawn skeleton, not line art.

Every bone is a FILLED shape with a gradient and a hairline stroke. An earlier
version stroked thin open outlines; at display size that read as cheap clip-art,
because real anatomical illustration gets its weight from mass, not from lines.

All geometry derives from the LANDMARKS below, so the bones, the joint hotspots
and the label leaders can never drift apart. Move a landmark and everything that
attaches to it follows.
"""
import math

# ---------------------------------------------------------------------------
# Landmarks — a ~7.9-head figure, the classical illustration proportion
# ---------------------------------------------------------------------------
VB_W, VB_H = 500, 830
CX = 250

CROWN, CHIN = 26, 122            # head = 96 tall
JAW_W = 30
NECK_BOT = 150

SHOULDER_Y, SHOULDER_DX = 174, 72
ELBOW_Y, ELBOW_DX = 322, 80
WRIST_Y, WRIST_DX = 448, 88
HAND_BOT = 492

RIB_TOP, RIB_BOT = 178, 314
LUMBAR_BOT = 376
PELVIS_TOP, PELVIS_BOT = 368, 456
HIP_Y, HIP_DX = 434, 36

KNEE_Y, KNEE_DX = 598, 40
ANKLE_Y, ANKLE_DX = 750, 42
FOOT_BOT, FOOT_FWD = 788, 34


def _f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def _poly(points, close=True):
    """Smooth a point list into a path using midpoint quadratics — gives bone
    outlines their organic curvature without hand-authoring every control point."""
    if not points:
        return ""
    d = f"M{_f(points[0][0])},{_f(points[0][1])}"
    for i in range(1, len(points) - 1):
        x0, y0 = points[i]
        mx, my = (points[i][0] + points[i + 1][0]) / 2, (points[i][1] + points[i + 1][1]) / 2
        d += f" Q{_f(x0)},{_f(y0)} {_f(mx)},{_f(my)}"
    d += f" L{_f(points[-1][0])},{_f(points[-1][1])}"
    return d + ("Z" if close else "")


def bone(x1, y1, x2, y2, profile):
    """A long bone as a closed filled outline.

    profile is [(t, half_width)] from proximal to distal; the flared ends and
    waisted shaft of a real diaphysis come straight out of that width curve.
    """
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    px, py = -dy / L, dx / L          # unit normal
    left, right = [], []
    for t, w in profile:
        cx, cy = x1 + dx * t, y1 + dy * t
        left.append((cx + px * w, cy + py * w))
        right.append((cx - px * w, cy - py * w))
    pts = left + list(reversed(right))
    return f'<path class="bn" d="{_poly(pts)}"/>'


def _ellipse(cx, cy, rx, ry, cls="bn"):
    return f'<ellipse class="{cls}" cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(rx)}" ry="{_f(ry)}"/>'


# ---------------------------------------------------------------------------
# Regions
# ---------------------------------------------------------------------------

def _skull():
    y = CROWN
    top = y
    brow = y + 50
    cheek = y + 68
    jaw = CHIN
    p = []
    # cranial vault + midface, one silhouette; the mandible is drawn separately
    p.append(
        '<path class="bn" d="'
        f'M{CX - 34},{brow + 2} '
        f'C{CX - 36},{top + 15} {CX - 21},{top} {CX},{top} '
        f'C{CX + 21},{top} {CX + 36},{top + 15} {CX + 34},{brow + 2} '
        f'C{CX + 33},{cheek - 2} {CX + 27},{cheek + 6} {CX + 20},{cheek + 11} '
        f'L{CX + 17},{jaw - 12} L{CX - 17},{jaw - 12} '
        f'L{CX - 20},{cheek + 11} '
        f'C{CX - 27},{cheek + 6} {CX - 33},{cheek - 2} {CX - 34},{brow + 2}Z"/>'
    )
    # mandible — a separate bone, which is what stops it reading as a Halloween mask
    p.append(
        '<path class="bn" d="'
        f'M{CX - 19},{cheek + 6} '
        f'L{CX - 17},{jaw - 9} '
        f'C{CX - 14},{jaw} {CX + 14},{jaw} {CX + 17},{jaw - 9} '
        f'L{CX + 19},{cheek + 6} '
        f'L{CX + 15},{cheek + 5} L{CX + 13},{jaw - 12} '
        f'C{CX + 8},{jaw - 6} {CX - 8},{jaw - 6} {CX - 13},{jaw - 12} '
        f'L{CX - 15},{cheek + 5}Z"/>'
    )
    # orbits — angled almonds, not round holes
    for s in (-1, 1):
        p.append(
            f'<path class="socket" d="'
            f'M{CX + s * 8},{brow + 1} '
            f'C{CX + s * 9},{brow + 8} {CX + s * 17},{brow + 10} {CX + s * 20},{brow + 4} '
            f'C{CX + s * 22},{brow - 3} {CX + s * 16},{brow - 8} {CX + s * 11},{brow - 5}Z"/>'
        )
    # nasal aperture
    p.append(f'<path class="socket" d="M{CX},{brow + 10} L{CX - 4.5},{cheek + 4} '
             f'Q{CX},{cheek + 7} {CX + 4.5},{cheek + 4}Z"/>')
    # upper dentition + coronal suture
    p.append(f'<path class="hair" d="M{CX - 13},{cheek + 12} Q{CX},{cheek + 16} {CX + 13},{cheek + 12}"/>')
    p.append(f'<path class="hair" d="M{CX - 30},{top + 26} Q{CX},{top + 17} {CX + 30},{top + 26}"/>')
    p.append(f'<path class="hair" d="M{CX + 1},{top + 4} Q{CX + 5},{top + 16} {CX + 1},{top + 24}"/>')
    return p


def _spine():
    """Cervical, thoracic and lumbar bodies as discrete stacked vertebrae. The
    cervical run matters most visually — without it the skull floats."""
    p = []
    cerv = [(CHIN + 6 + i * 9.2, 9.0 - i * 0.2, 3.6) for i in range(5)]
    thor = [(RIB_TOP + 6 + i * 10.6, 8.0, 3.7) for i in range(12)]
    lumb = [(RIB_BOT + 8 + i * 12.6, 10.6, 5.2) for i in range(4)]
    for cy, rx, ry in cerv + thor + lumb:
        p.append(_ellipse(CX, cy, rx, ry))
    # Deliberately no transverse-process lines: hairlines between every body
    # turned the neck into a coil spring.
    return p


def _ribcage():
    """Twelve pairs sweeping down and forward off the thoracic spine, longest
    at rib 7 — the taper top and bottom is what makes a cage look like a cage."""
    p = []
    sternum_top, sternum_bot = RIB_TOP + 12, RIB_BOT - 12
    for i in range(12):
        t = i / 11.0
        y0 = RIB_TOP + 4 + i * 11.0                       # vertebral origin
        span = math.sin(math.pi * (0.30 + 0.62 * t)) * 74  # widest mid-cage
        if i >= 9:
            span *= 1.0 - (i - 8) * 0.17                   # floating ribs pull in
        drop = 26 + t * 30
        for s in (-1, 1):
            x_end = CX + s * (span * 0.52)
            y_end = y0 + drop
            p.append(
                f'<path class="rib" d="'
                f'M{CX + s * 8},{_f(y0)} '
                f'C{CX + s * (span * 0.72)},{_f(y0 + 2)} '
                f'{CX + s * (span * 0.62)},{_f(y0 + drop * 0.72)} '
                f'{_f(x_end)},{_f(y_end)}"/>'
            )
            # A costal-cartilage run was tried here and removed: at this scale the
            # extra strokes closed the gap between the ribs and the sternum into
            # a solid ladder, which is the single thing that made the cage read
            # as clip-art. The open anterior gap is what gives it depth.
    # sternum: manubrium, body, xiphoid
    p.append(f'<path class="bn" d="M{CX - 9},{sternum_top} Q{CX},{sternum_top - 4} {CX + 9},{sternum_top} '
             f'L{CX + 7},{sternum_top + 22} L{CX - 7},{sternum_top + 22}Z"/>')
    p.append(f'<path class="bn" d="M{CX - 7},{sternum_top + 24} L{CX + 7},{sternum_top + 24} '
             f'L{CX + 5},{sternum_bot - 8} L{CX - 5},{sternum_bot - 8}Z"/>')
    p.append(f'<path class="bn" d="M{CX - 4},{sternum_bot - 6} L{CX + 4},{sternum_bot - 6} '
             f'L{CX},{sternum_bot + 5}Z"/>')
    return p


def _scapulae():
    """Drawn BEFORE the rib cage so they sit behind it. Painted on top they read
    as wings bolted to the chest."""
    p = []
    for s in (-1, 1):
        ax = CX + s * SHOULDER_DX
        p.append(
            f'<path class="scap" d="'
            f'M{_f(ax - s * 6)},{SHOULDER_Y + 6} '
            f'C{CX + s * 44},{SHOULDER_Y + 20} {CX + s * 40},{SHOULDER_Y + 44} '
            f'{CX + s * 30},{SHOULDER_Y + 56} '
            f'C{CX + s * 26},{SHOULDER_Y + 44} {CX + s * 27},{SHOULDER_Y + 22} '
            f'{CX + s * 24},{SHOULDER_Y + 12}Z"/>'
        )
    return p


def _clavicles():
    p = []
    for s in (-1, 1):
        ax = CX + s * SHOULDER_DX
        # the S-curve is the giveaway detail
        p.append(
            f'<path class="clav" d="'
            f'M{CX + s * 6},{SHOULDER_Y - 1} '
            f'C{CX + s * 24},{SHOULDER_Y - 8} {CX + s * 46},{SHOULDER_Y - 3} '
            f'{_f(ax - s * 5)},{SHOULDER_Y + 1}"/>'
        )
        p.append(_ellipse(ax, SHOULDER_Y + 7, 8, 7))   # glenohumeral head
    return p


def _pelvis():
    """Iliac crest flares up and OUT to a corner, then the wing narrows sharply
    into the acetabulum. Rounded wings read as two blobs, which is the trap."""
    p = []
    top, bot = PELVIS_TOP, PELVIS_BOT
    for s in (-1, 1):
        p.append(
            f'<path class="bn" d="'
            f'M{CX + s * 7},{top + 4} '                                   # sacral join
            f'C{CX + s * 26},{top - 6} {CX + s * 46},{top - 4} {CX + s * 55},{top + 10} '  # crest
            f'C{CX + s * 60},{top + 22} {CX + s * 55},{top + 34} {CX + s * 47},{top + 42} '  # outer wing
            f'C{CX + s * 44},{top + 56} {CX + s * 44},{top + 66} {CX + s * 36},{top + 72} '  # to acetabulum
            f'C{CX + s * 27},{top + 78} {CX + s * 19},{top + 70} {CX + s * 18},{top + 58} '  # ischium
            f'C{CX + s * 17},{top + 40} {CX + s * 12},{top + 20} {CX + s * 7},{top + 4}Z"/>'
        )
        # obturator foramen — the hole that makes a pelvis unmistakable
        p.append(
            f'<path class="socket" d="'
            f'M{CX + s * 24},{top + 46} '
            f'C{CX + s * 23},{top + 60} {CX + s * 32},{top + 66} {CX + s * 37},{top + 58} '
            f'C{CX + s * 40},{top + 48} {CX + s * 33},{top + 41} {CX + s * 26},{top + 42}Z"/>'
        )
        p.append(_ellipse(CX + s * HIP_DX, HIP_Y, 9.5, 8.5))   # acetabulum + femoral head
    # sacrum tapering to the coccyx
    p.append(f'<path class="bn" d="M{CX - 11},{top + 2} L{CX + 11},{top + 2} '
             f'L{CX + 7},{top + 44} Q{CX},{top + 54} {CX - 7},{top + 44}Z"/>')
    for i in range(2):
        p.append(f'<path class="hair" d="M{CX - 7 + i},{top + 17 + i * 13} L{CX + 7 - i},{top + 17 + i * 13}"/>')
    p.append(f'<path class="hair" d="M{CX},{bot - 12} L{CX},{bot - 2}"/>')   # pubic symphysis
    return p


def _arms():
    p = []
    for s in (-1, 1):
        sx, ex = CX + s * SHOULDER_DX, CX + s * ELBOW_DX
        wx = CX + s * WRIST_DX
        # humerus
        p.append(bone(sx, SHOULDER_Y + 6, ex, ELBOW_Y,
                      [(0, 8.5), (0.06, 7.4), (0.2, 5.0), (0.5, 4.5),
                       (0.8, 5.2), (0.93, 7.8), (1, 6.8)]))
        # ulna (olecranon at the elbow) + radius
        p.append(bone(ex - s * 3, ELBOW_Y - 4, wx - s * 4, WRIST_Y,
                      [(0, 6.4), (0.08, 4.6), (0.4, 3.4), (0.8, 3.0), (1, 4.2)]))
        p.append(bone(ex + s * 5, ELBOW_Y + 6, wx + s * 4, WRIST_Y,
                      [(0, 3.4), (0.3, 3.0), (0.7, 3.4), (1, 5.0)]))
        # carpus
        p.append(_ellipse(wx, WRIST_Y + 8, 9, 6.5))
        # metacarpals + phalanges — five rays, splayed
        for k in range(5):
            a = -0.34 + k * 0.17
            mx = wx + math.sin(a) * 13 + s * 1.5
            my = WRIST_Y + 14 + math.cos(a) * 4
            tipx = wx + math.sin(a) * 21
            tipy = my + 15 + (0 if k in (2, 3) else -3)
            p.append(f'<path class="digit" d="M{_f(mx)},{_f(my)} L{_f(tipx)},{_f(tipy)}"/>')
            p.append(f'<path class="digit" d="M{_f(tipx)},{_f(tipy)} '
                     f'L{_f(tipx + math.sin(a) * 7)},{_f(min(tipy + 9, HAND_BOT))}"/>')
    return p


def _legs():
    p = []
    for s in (-1, 1):
        hx = CX + s * HIP_DX
        kx = CX + s * KNEE_DX
        ax = CX + s * ANKLE_DX
        # femur — offset neck into the acetabulum, then the long shaft
        p.append(bone(hx, HIP_Y, kx, KNEE_Y,
                      [(0, 10.0), (0.06, 8.4), (0.22, 6.0), (0.5, 5.6),
                       (0.78, 6.6), (0.92, 9.8), (1, 8.6)]))
        p.append(_ellipse(kx, KNEE_Y + 12, 6.5, 5))          # patella
        # tibia + fibula
        p.append(bone(kx - s * 2, KNEE_Y + 20, ax, ANKLE_Y,
                      [(0, 6.0), (0.04, 8.6), (0.14, 6.8), (0.44, 4.8), (0.78, 4.2), (0.93, 5.6), (1, 5.0)]))
        p.append(bone(kx + s * 9, KNEE_Y + 24, ax + s * 6, ANKLE_Y - 4,
                      [(0, 2.4), (0.05, 3.8), (0.3, 2.6), (0.75, 2.6), (1, 4.0)]))
        # talus / calcaneus and the forefoot rays
        p.append(_ellipse(ax, ANKLE_Y + 9, 8.5, 6.5))
        p.append(
            f'<path class="bn" d="'
            f'M{_f(ax - s * 8)},{ANKLE_Y + 12} '
            f'Q{_f(ax - s * 11)},{FOOT_BOT} {_f(ax - s * 2)},{FOOT_BOT} '
            f'L{_f(ax + s * FOOT_FWD)},{FOOT_BOT - 2} '
            f'Q{_f(ax + s * (FOOT_FWD + 4))},{FOOT_BOT - 9} {_f(ax + s * FOOT_FWD)},{FOOT_BOT - 12} '
            f'L{_f(ax + s * 6)},{ANKLE_Y + 15}Z"/>'
        )
        for k in range(4):
            fx = ax + s * (14 + k * 6)
            p.append(f'<path class="hair" d="M{_f(fx)},{FOOT_BOT - 12} L{_f(fx + s * 3)},{FOOT_BOT - 3}"/>')
    return p


def skeleton_svg():
    # order IS the depth: scapulae behind the cage, clavicles in front of it
    parts = (_scapulae() + _spine() + _ribcage() + _clavicles() + _pelvis()
             + _arms() + _legs() + _skull())
    return "\n      ".join(parts)


def defs():
    """Gradients and the soft gold bloom that gives the bones physical presence."""
    return f"""<linearGradient id="boneFill" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#FDF2CE"/>
        <stop offset=".42" stop-color="#F3D98A"/>
        <stop offset="1" stop-color="#D9AA35"/>
      </linearGradient>
      <linearGradient id="boneFillSoft" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#E7CE8E"/>
        <stop offset="1" stop-color="#C79B31"/>
      </linearGradient>
      <radialGradient id="figGlow" cx=".5" cy=".42" r=".62">
        <stop offset="0" stop-color="#FDC929" stop-opacity=".14"/>
        <stop offset=".55" stop-color="#12457F" stop-opacity=".10"/>
        <stop offset="1" stop-color="#12457F" stop-opacity="0"/>
      </radialGradient>
      <filter id="boneBloom" x="-25%" y="-25%" width="150%" height="150%">
        <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#FDC929" flood-opacity=".34"/>
      </filter>"""
