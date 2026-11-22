"""Classroom set (added for the Einstein-at-the-blackboard Short). Same plane conventions as interiors.py.

classroom(mood, view='board', board='table', desk=False)
  view 'board' : the blackboard wall (teal wainscot, cream plaster, window, door, clock, pendant lamps)
  view 'class' : reverse shot toward the students' wall (3 windows, cork board, map, door) with two rows of desks.
                 Cast kids so their feet sit ~75-105 px below the desk top: the desk front hides their legs.
  board        : 'line'  = only the wrong line 9 x 10 = 91, big, in yellow chalk
                 'table' = the nine good lines in white + the wrong tenth line in yellow
                 'ticks' = like table, plus green ticks on the nine good lines and a red circle round the tenth
  desk         : board view only; adds a student desk in the foreground (z 0.9) for a seated kid behind it
"""
import math

import skia

from .paint import (fill, stroke, ink, shade, mix, path_poly, path_smooth, rrect, ellipse, blurred, lin_grad, rad_grad,
                    argb, rng, surface, draw_tex_quad, INK)
from . import textures as tx
from . import setkit as sk
from .light import MOODS, halo, pool, god_rays, window_slash
from .text import draw_text
from .interiors import room_box

CREAM = '#efd8a8'
TEAL = '#3e7c82'
WOOD = '#a8683a'


def _plaster(w, h, base=CREAM, seed=1):
    s = surface(w, h, base)
    c = s.getCanvas()
    p = skia.Paint(AntiAlias=True)
    p.setShader(lin_grad((0, 0), (0, h), [argb('#ffffff', 0.16), argb('#ffffff', 0), argb('#4a2e66', 0.10)], [0, 0.45, 1]))
    c.drawRect(skia.Rect.MakeWH(w, h), p)
    r = rng(seed)
    for _ in range(70):
        x, y = r.uniform(0, w), r.uniform(0, h)
        c.drawLine(x, y, x + r.uniform(40, 200), y + r.uniform(-10, 10), stroke(shade(base, r.uniform(-0.16, 0.1)), r.uniform(6, 18), 0.07))
    return s.makeImageSnapshot()


def _chalk(cv, s, cx, base, size, col, angle=0.0, a=0.93):
    cv.save(); cv.translate(cx, base); cv.rotate(angle)
    cv.save(); cv.translate(0, -size * 0.3)
    draw_text(cv, s, 0, size * 0.3, size, col)       # chalk text
    cv.restore()
    cv.restore()


def _chalk_text(cv, s, cx, base, size, col, angle=0.0):
    """Chalk look: a soft dusty halo under the lettering, then the lettering itself (slightly translucent)."""
    cv.save(); cv.translate(cx, base); cv.rotate(angle)
    from .text import font
    f = font(size)
    w = f.measureText(s)
    blob = skia.TextBlob.MakeFromString(s, f)
    pd = skia.Paint(AntiAlias=True); pd.setColor(skia.Color4f(1, 1, 1, 0.22)); pd.setStyle(skia.Paint.kStroke_Style); pd.setStrokeWidth(5)
    blurred(pd, 2.5)
    cv.drawTextBlob(blob, -w / 2, 0, pd)
    pm = fill(col, 0.94)
    cv.drawTextBlob(blob, -w / 2, 0, pm)
    cv.restore()


def _tick(cv, x, y, s=1.0, col='#7be08a'):
    pth = path_smooth([(x - 14 * s, y - 2 * s), (x - 4 * s, y + 11 * s), (x + 16 * s, y - 20 * s)], close=False, tension=0.3)
    cv.drawPath(pth, stroke(col, 7 * s, 0.95))


def _blackboard(cv, board, bx=250, by=380, bw=580, bh=560):
    # wooden frame + slate + dust smears
    cv.drawPath(rrect(bx - 20, by - 20, bw + 40, bh + 40, 10), fill('#9a6238'))
    cv.drawPath(rrect(bx - 20, by - 20, bw + 40, bh + 40, 10), ink(5))
    cv.drawPath(rrect(bx - 20, by - 20, bw + 40, 12, 6), fill('#c08a54', 0.8))
    slate = skia.Rect.MakeXYWH(bx, by, bw, bh)
    p = skia.Paint(AntiAlias=True)
    p.setShader(lin_grad((bx, by), (bx + bw, by + bh), [argb('#3b6a56'), argb('#2c5846'), argb('#264c3d')]))
    cv.drawRect(slate, p)
    cv.save(); cv.clipRect(slate)
    r = rng(8)
    for _ in range(26):                                   # old wiped chalk smears
        x, y = r.uniform(bx, bx + bw), r.uniform(by, by + bh)
        pp = fill('#e8f0e4', r.uniform(0.04, 0.09)); blurred(pp, 7)
        cv.save(); cv.translate(x, y); cv.rotate(r.uniform(-25, 25))
        cv.drawPath(ellipse(0, 0, r.uniform(60, 170), r.uniform(14, 30)), pp)
        cv.restore()
    ink_w = '#f4f2e6'
    cx = bx + bw / 2
    if board == 'line':
        _chalk_text(cv, '9 \u00d7 10 = 91', cx, by + bh * 0.56, 76, '#f8e47a', angle=-2.2)
        cv.drawPath(path_smooth([(cx - 230, by + bh * 0.56 + 30), (cx - 80, by + bh * 0.56 + 38), (cx + 120, by + bh * 0.56 + 26), (cx + 235, by + bh * 0.56 + 36)], close=False),
                    stroke('#f8e47a', 5, 0.85))
    else:
        for n in range(1, 10):
            y = by + 62 + (n - 1) * 50
            _chalk_text(cv, '9 \u00d7 %d = %d' % (n, 9 * n), cx + 14, y, 40, ink_w, angle=-0.6)
            if board == 'ticks':
                _tick(cv, bx + 62, y - 10, 1.0)
        y10 = by + 62 + 9 * 50
        _chalk_text(cv, '9 \u00d7 10 = 91', cx + 14, y10, 42, '#f8e47a', angle=-0.6)
        cv.drawPath(path_smooth([(cx - 120, y10 + 12), (cx, y10 + 18), (cx + 140, y10 + 10)], close=False), stroke('#f8e47a', 4, 0.8))
        if board == 'ticks':
            ring = skia.Path(); ring.addOval(skia.Rect.MakeLTRB(cx - 172, y10 - 48, cx + 196, y10 + 26))
            cv.drawPath(ring, stroke('#ff8f8f', 7, 0.95))
    cv.restore()
    cv.drawRect(slate, ink(4))
    # chalk tray with chalk + felt eraser
    cv.drawPath(rrect(bx - 10, by + bh + 4, bw + 20, 26, 6), fill('#b27a46'))
    cv.drawPath(rrect(bx - 10, by + bh + 4, bw + 20, 26, 6), ink(4))
    for k, (dx, col) in enumerate(((40, '#fdfaf0'), (86, '#f8e47a'), (120, '#ff9ab0'))):
        cv.drawPath(rrect(bx + dx, by + bh - 10, 44, 14, 6), fill(col)); cv.drawPath(rrect(bx + dx, by + bh - 10, 44, 14, 6), ink(2.4))
    cv.drawPath(rrect(bx + bw - 150, by + bh - 24, 96, 28, 5), fill('#d86a4a')); cv.drawPath(rrect(bx + bw - 150, by + bh - 24, 96, 28, 5), ink(3))
    cv.drawRect(skia.Rect.MakeXYWH(bx + bw - 150, by + bh - 8, 96, 12), fill('#6a4a3a')); cv.drawRect(skia.Rect.MakeXYWH(bx + bw - 150, by + bh - 8, 96, 12), ink(2.4))


def _pendant(cv, lx, E, ly=176):
    cv.drawLine(lx, -500, lx, ly - 70, stroke('#2a2232', 5))
    sh = path_poly([(lx - 76, ly), (lx + 76, ly), (lx + 42, ly - 62), (lx - 42, ly - 62)])
    cv.drawPath(sh, fill('#3f8a6a')); cv.drawPath(sh, ink(3.5))
    cv.drawPath(ellipse(lx, ly + 2, 76, 12), fill('#fff0c0'))
    E.append(dict(kind='lamp', pos=(lx, ly + 6), r=240, lit=True, ground=None))


def _wainscot(cv, x0, x1, y0, y1):
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), fill(TEAL))
    x = x0 + 20
    while x < x1:
        cv.drawLine(x, y0 + 14, x, y1, stroke(shade(TEAL, -0.3), 2, 0.5))
        x += 40
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y0 + 16), fill('#f2ead8')); cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y0 + 16), ink(3))
    cv.drawRect(skia.Rect.MakeLTRB(x0, y1 - 20, x1, y1), fill('#2a4a50')); cv.drawRect(skia.Rect.MakeLTRB(x0, y1 - 20, x1, y1), ink(3))


def _glass(m, mood):
    return {'night': '#26357e', 'golden': '#f2a850', 'sunset': '#e07a8a', 'dawn': '#c8a0d8'}.get(mood, m['sky'][1])


def _desk(cv, x, y_top, w, floor_y, col='#c28a52', depth=34):
    """Front-on school desk: top (slightly in perspective), apron, modesty panel and metal legs."""
    top = path_poly([(x - w * 0.43, y_top), (x + w * 0.43, y_top), (x + w * 0.5, y_top + depth), (x - w * 0.5, y_top + depth)])
    # legs / panel behind the front edge
    cv.drawPath(rrect(x - w * 0.46, y_top + depth, w * 0.92, floor_y - y_top - depth - 8, 6), fill(shade(col, -0.35)))
    cv.drawPath(rrect(x - w * 0.46, y_top + depth, w * 0.92, floor_y - y_top - depth - 8, 6), ink(4))
    for sx in (-1, 1):
        cv.drawRect(skia.Rect.MakeXYWH(x + sx * w * 0.44 - 6, y_top + depth, 12, floor_y - y_top - depth + 6), fill('#4a4a5e'))
        cv.drawRect(skia.Rect.MakeXYWH(x + sx * w * 0.44 - 6, y_top + depth, 12, floor_y - y_top - depth + 6), ink(2.6))
    cv.drawPath(top, fill(col)); cv.drawPath(top, ink(4.5))
    cv.drawPath(path_poly([(x - w * 0.4, y_top + 6), (x + w * 0.1, y_top + 6), (x + w * 0.12, y_top + 14), (x - w * 0.42, y_top + 14)]), fill('#ffffff', 0.22))
    cv.drawRect(skia.Rect.MakeXYWH(x - w * 0.5, y_top + depth, w, 14), fill(shade(col, -0.2)))
    cv.drawRect(skia.Rect.MakeXYWH(x - w * 0.5, y_top + depth, w, 14), ink(3.5))


def _paper_and_pencil(cv, x, y, s=1.0, seed=0):
    r = rng(seed)
    cv.save(); cv.translate(x, y); cv.rotate(r.uniform(-8, 8)); cv.scale(s, s)
    cv.drawPath(rrect(-46, -8, 92, 24, 3), fill('#f8f4ec')); cv.drawPath(rrect(-46, -8, 92, 24, 3), ink(2.6))
    cv.drawLine(-34, 4, 20, 4, stroke('#8a8a9a', 2)); cv.drawLine(-34, 11, 4, 11, stroke('#8a8a9a', 2))
    cv.drawPath(rrect(26, -14, 52, 10, 4), fill('#f2c640')); cv.drawPath(rrect(26, -14, 52, 10, 4), ink(2.2))
    cv.restore()


def classroom(mood, view='board', board='table', desk=False):
    m = MOODS[mood]
    night = mood == 'night'
    E = []
    glass = _glass(m, mood)
    if view == 'class':
        return _class_view(mood, m, night, E, glass)

    back = (60, 170, 1020, 1240)

    def room(cv):
        room_box(cv, back, back_tex=_plaster(960, 1070, CREAM, 2),
                 left_tex=_plaster(1200, 1600, '#e3c690', 3), right_tex=_plaster(1200, 1600, '#e3c690', 4),
                 floor_tex=tx.wood_planks(1400, 1400, plank=130, base='#b17f4c', vertical=True, seed=5, nails=False),
                 ceil_tex=tx.ceiling_tiles(1400, 1200, size=170, base='#ebe4d6'),
                 right_shade=0.2, left_shade=0.1)
        _wainscot(cv, 60, 1020, 1000, 1240)
        # window (left of the board) with a mood sky
        wx, wy, ww, wh = 98, 400, 112, 520
        sk.window(cv, wx, wy, ww, wh, frame='#f4efe4', glass=glass, curtain=None, panes=(2, 4), E=E, lit=not night)
        sk.plant_pot(cv, 154, 1004, 1.0, seed=3)
        # door (right of the board), glass pane
        sk.door(cv, 884, 560, 112, 680, col=WOOD, frame='#f4efe4', glass=True, E=E, lit=not night)
        # sign, clock, calendar, picture
        from . import props as pr
        pr.sign_board(cv, 540, 336, 'MATHS', s=0.4, col='#2f4a3a', txt='#f2c640', post=False)
        sk.wall_clock(cv, 880, 290, 50)
        sk.calendar(cv, 112, 215, 92, 118, month='MAI', day='12')
        _blackboard(cv, board)
        # set square + ruler leaning on the wall by the door
        cv.drawPath(path_poly([(848, 900), (848, 1010), (780, 1010)]), stroke('#e6b43c', 7)); cv.drawPath(path_poly([(848, 900), (848, 1010), (780, 1010)]), ink(3))
        # teacher's desk (back right) with books + apple
        _desk(cv, 700, 1128, 320, 1252, col='#b27a46', depth=26)
        for k, (bw_, col) in enumerate(((120, '#c8483a'), (104, '#3f78c8'), (112, '#e6b43c'))):
            cv.drawPath(rrect(612 + k * 3, 1096 - k * 17, bw_, 17, 3), fill(col)); cv.drawPath(rrect(612 + k * 3, 1096 - k * 17, bw_, 17, 3), ink(2.4))
        cv.drawCircle(770, 1086, 20, fill('#d83a3a')); cv.drawCircle(770, 1086, 20, ink(3)); cv.drawLine(770, 1068, 776, 1052, stroke('#5a3a22', 4))
        # pendant lamps
        for lx in (300, 780):
            _pendant(cv, lx, E)

    def near(cv):
        # blurred foreground: a student desk corner with an apple and a stack of books at the lens
        cv.drawPath(rrect(-260, 1720, 760, 400, 24), fill('#c28a52')); cv.drawPath(rrect(-260, 1720, 760, 400, 24), ink(7))
        cv.drawRect(skia.Rect.MakeXYWH(-260, 1720, 760, 34), fill('#e0aa74')); cv.drawCircle(230, 1700, 64, fill('#d83a3a')); cv.drawCircle(230, 1700, 64, ink(6))
        cv.drawLine(230, 1640, 252, 1590, stroke('#5a3a22', 8))
        for k, col in enumerate(('#3f78c8', '#2f9a5a', '#e6b43c')):
            cv.drawPath(rrect(780 - k * 6, 1820 - k * 52, 400, 50, 8), fill(col)); cv.drawPath(rrect(780 - k * 6, 1820 - k * 52, 400, 50, 8), ink(6))

    def student_desk(cv):
        _desk(cv, 540, 1570, 560, 1800, col='#c28a52', depth=44)
        _paper_and_pencil(cv, 470, 1584, 1.5, seed=3)

    def lights(cv, mm):
        sk.draw_emitters(cv, E, mm, night)
        key = mm['key']
        if night:
            halo(cv, 154, 660, 300, (130, 150, 255), 0.22, hot=False)           # moonlight through the window
            for k in range(5):
                y = 1260 + k * 120
                window_slash(cv, [(60, y), (360, y - 40), (390, y - 14), (70, y + 40)], (120, 140, 255), 0.07)
        else:
            a = {'day': 0.16, 'interior': 0.10, 'golden': 0.22, 'sunset': 0.3, 'dawn': 0.18}.get(mood, 0.15)
            for k in range(3):
                y = 1290 + k * 150
                window_slash(cv, [(70, y), (520, y - 60 + k * 10), (580, y - 20 + k * 14), (80, y + 64)], key, a)
            if mood in ('sunset', 'golden', 'dawn'):
                god_rays(cv, (154, 650), 8, 55, 1500, n=9, col=key, a=0.16 if mood != 'golden' else 0.12)
        if mood == 'golden':
            for (gx, gy_, gr) in ((540, 690, 560), (540, 820, 380)):
                p = skia.Paint(AntiAlias=True)
                p.setShader(rad_grad((gx, gy_), gr, [argb((255, 214, 120), 0.5), argb((255, 190, 90), 0.16), argb((255, 190, 90), 0)], [0, 0.45, 1]))
                p.setBlendMode(skia.BlendMode.kScreen)
                cv.drawCircle(gx, gy_, gr, p)
            god_rays(cv, (540, 700), -90, 360, 900, n=16, col=(255, 226, 150), a=0.14, width=0.7)
            rr = rng(11)
            for k in range(40):
                halo(cv, rr.uniform(120, 960), rr.uniform(430, 1100), rr.uniform(6, 16), (255, 236, 170), 0.8)

    planes = [('room', 1.5, room, dict(lights=lights))]
    if desk:
        planes.append(('desk', 0.92, student_desk, dict()))
    planes.append(('near', 0.6, near, dict(blur=12)))
    return planes, dict(ground_y=1300, board=(540, 660), desk=(540, 1570))


# =============================================================================== reverse shot: the class
def _map(cv, x, y, w, h):
    cv.drawPath(rrect(x, y, w, h, 5), fill('#f4ecd8')); cv.drawPath(rrect(x, y, w, h, 5), ink(4))
    cv.drawRect(skia.Rect.MakeXYWH(x + 8, y + 8, w - 16, h - 16), fill('#7fb6e0'))
    for (cx, cy, rw, rh, col) in ((0.28, 0.4, 0.22, 0.3, '#6fae56'), (0.62, 0.34, 0.2, 0.22, '#c8b25a'), (0.7, 0.68, 0.16, 0.2, '#6fae56'), (0.4, 0.74, 0.1, 0.12, '#c8b25a')):
        cv.drawPath(path_smooth([(x + w * (cx - rw / 2), y + h * cy), (x + w * cx, y + h * (cy - rh / 2)), (x + w * (cx + rw / 2), y + h * cy), (x + w * cx, y + h * (cy + rh / 2))]), fill(col))
    cv.drawRect(skia.Rect.MakeXYWH(x + 8, y + 8, w - 16, h - 16), ink(2.4))


def _class_view(mood, m, night, E, glass):
    back = (40, 300, 1040, 1060)

    def room(cv):
        room_box(cv, back, back_tex=_plaster(1000, 760, '#f0dcae', 6),
                 left_tex=_plaster(1200, 1600, '#e3c690', 7), right_tex=_plaster(1200, 1600, '#e3c690', 8),
                 floor_tex=tx.wood_planks(1400, 1400, plank=130, base='#b17f4c', vertical=True, seed=9, nails=False),
                 ceil_tex=tx.ceiling_tiles(1400, 1200, size=170, base='#ebe4d6'), right_shade=0.2, left_shade=0.1)
        _wainscot(cv, 40, 1040, 900, 1060)
        for k in range(3):
            sk.window(cv, 108 + k * 196, 430, 140, 330, frame='#f4efe4', glass=glass, curtain=None, panes=(2, 3), E=E, lit=not night)
        # cork board with notes
        cv.drawPath(rrect(690, 470, 190, 270, 8), fill('#c8965a')); cv.drawPath(rrect(690, 470, 190, 270, 8), ink(4.5))
        cols = ['#f8e070', '#a8d8f0', '#f8a0c0', '#f4f0e8', '#b8e0a0', '#f8c090']
        for k in range(6):
            nx, ny = 704 + (k % 2) * 88, 484 + (k // 2) * 84
            cv.drawRect(skia.Rect.MakeXYWH(nx, ny, 70, 62), fill(cols[k])); cv.drawRect(skia.Rect.MakeXYWH(nx, ny, 70, 62), ink(2))
            for j in range(3):
                cv.drawLine(nx + 9, ny + 18 + j * 12, nx + 56 - j * 8, ny + 18 + j * 12, stroke('#6a6a7a', 2))
            cv.drawCircle(nx + 35, ny + 6, 5, fill(['#d8483a', '#3f6ac8', '#2f9a5a'][k % 3]))
        _map(cv, 128, 330, 190, 80)
        sk.wall_clock(cv, 560, 365, 48)
        sk.door(cv, 906, 500, 100, 560, col=WOOD, frame='#f4efe4', glass=True, E=E, lit=not night)
        sk.plant_pot(cv, 120, 1050, 1.3, seed=5)
        for lx in (300, 780):
            _pendant(cv, lx, E)

    def rows_far(cv):
        for x in (190, 540, 890):
            _desk(cv, x, 1170, 270, 1290, col='#c28a52', depth=30)
        for k, x in enumerate((190, 540, 890)):
            _paper_and_pencil(cv, x - 30, 1176, 0.85, seed=k)

    def rows_near(cv):
        for x in (320, 780):
            _desk(cv, x, 1560, 400, 1790, col='#c28a52', depth=44)
        for k, x in enumerate((320, 780)):
            _paper_and_pencil(cv, x - 40, 1574, 1.3, seed=k + 4)

    def near(cv):
        cv.drawPath(rrect(-300, 1790, 760, 420, 24), fill('#c28a52')); cv.drawPath(rrect(-300, 1790, 760, 420, 24), ink(7))
        cv.drawRect(skia.Rect.MakeXYWH(-300, 1790, 760, 36), fill('#e0aa74'))
        cv.drawPath(rrect(840, 1850, 420, 300, 20), fill('#c28a52')); cv.drawPath(rrect(840, 1850, 420, 300, 20), ink(7))

    def lights(cv, mm):
        sk.draw_emitters(cv, E, mm, night)
        key = mm['key']
        if night:
            for k in range(3):
                halo(cv, 178 + k * 196, 595, 190, (130, 150, 255), 0.16, hot=False)
        else:
            a = {'day': 0.16, 'interior': 0.12, 'golden': 0.22, 'sunset': 0.3, 'dawn': 0.18}.get(mood, 0.15)
            for k in range(3):
                x = 140 + k * 196
                window_slash(cv, [(x, 1090 + 20 * k), (x + 150, 1090 + 20 * k), (x + 330, 1480), (x + 60, 1480)], key, a)
            if mood in ('sunset', 'golden', 'dawn'):
                for k in range(3):
                    god_rays(cv, (178 + k * 196, 600), 90, 28, 1200, n=5, col=key, a=0.12, seed=3 + k)

    return [
        ('room', 1.6, room, dict(lights=lights)),
        ('rows_far', 1.2, rows_far, dict()),
        ('rows_near', 0.92, rows_near, dict()),
        ('near', 0.6, near, dict(blur=12)),
    ], dict(ground_y=1300, far_desk_top=1170, near_desk_top=1560)