from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output" / "pdf"
OUT_FILE = OUT_DIR / "一年级数学下册期末模拟真题卷.pdf"

PAGE_W, PAGE_H = landscape(A4)
MARGIN_X = 36
MARGIN_Y = 34
GUTTER = 26
COL_W = (PAGE_W - 2 * MARGIN_X - GUTTER) / 2
LEFT_X = MARGIN_X
RIGHT_X = MARGIN_X + COL_W + GUTTER
TOP_Y = PAGE_H - MARGIN_Y


def setup_fonts():
    font_dir = Path("C:/Windows/Fonts")
    fonts = {
        "Song": font_dir / "simsun.ttc",
        "Hei": font_dir / "simhei.ttf",
        "Kai": font_dir / "simkai.ttf",
    }
    for name, path in fonts.items():
        pdfmetrics.registerFont(TTFont(name, str(path)))


def text(c, x, y, s, size=12, font="Song", bold=False):
    c.setFont("Hei" if bold else font, size)
    c.drawString(x, y, s)


def centered(c, x, y, w, s, size=12, font="Hei"):
    c.setFont(font, size)
    c.drawCentredString(x + w / 2, y, s)


def wrapped(c, x, y, s, width, size=11, leading=19, first_indent=0):
    c.setFont("Song", size)
    line = ""
    cur_x = x + first_indent
    max_chars = max(8, int(width / (size * 0.92)))
    for ch in s:
        if ch == "\n":
            c.drawString(cur_x, y, line)
            y -= leading
            line = ""
            cur_x = x
            continue
        line += ch
        if len(line) >= max_chars:
            c.drawString(cur_x, y, line)
            y -= leading
            line = ""
            cur_x = x
    if line:
        c.drawString(cur_x, y, line)
        y -= leading
    return y


def blank_line(c, x, y, w=54, h=16):
    c.roundRect(x, y - 2, w, h, 3, stroke=1, fill=0)


def answer_boxes(c, x, y, count=3, box=17, gap=7):
    for i in range(count):
        c.roundRect(x + i * (box + gap), y, box, box, 3, stroke=1, fill=0)


def formula_boxes(c, x, y):
    answer_boxes(c, x, y, 1)
    c.circle(x + 31, y + 8.5, 8.5)
    answer_boxes(c, x + 46, y, 1)
    text(c, x + 70, y + 3, "=", 12)
    answer_boxes(c, x + 86, y, 1)
    text(c, x + 111, y + 3, "（    ）", 12)


def number_line(c, x, y, w=250, start=0, end=100, mark=None):
    c.line(x, y, x + w, y)
    c.line(x + w, y, x + w - 6, y + 4)
    c.line(x + w, y, x + w - 6, y - 4)
    for i in range(11):
        px = x + w * i / 10
        c.line(px, y - 5, px, y + 5)
    text(c, x - 3, y - 18, str(start), 10)
    text(c, x + w / 2 - 7, y - 18, str((start + end) // 2), 10)
    text(c, x + w - 12, y - 18, str(end), 10)
    if mark is not None:
        px = x + w * (mark - start) / (end - start)
        c.line(px, y - 12, px, y + 12)
        text(c, px - 5, y + 15, "▲", 12, "Hei")


def base_ten(c, x, y, tens=0, ones=0, scale=1.0):
    for i in range(tens):
        tx = x + i * 15 * scale
        for k in range(10):
            c.circle(tx + 4 * scale, y + k * 3.6 * scale, 1.25 * scale, stroke=1, fill=0)
        c.line(tx + 2 * scale, y - 1 * scale, tx + 8 * scale, y + 37 * scale)
    ox = x + tens * 15 * scale + 10 * scale
    for j in range(ones):
        c.roundRect(ox + j * 5 * scale, y, 2.7 * scale, 34 * scale, 1, stroke=1, fill=0)


def hundred_chart(c, x, y, center):
    size = 18
    offsets = [(0, 0), (size, 0), (size, -size), (2 * size, -size)]
    for dx, dy in offsets:
        c.rect(x + dx, y + dy, size, size)
    text(c, x + size + 4, y + 4, str(center), 10)


def wall(c, x, y, cols=8, rows=5, missing=(9, 18, 24)):
    bw, bh = 36, 13
    idx = 1
    for r in range(rows):
        off = 0 if r % 2 == 0 else bw / 2
        for col in range(cols):
            px = x + col * bw - off
            py = y - r * bh
            if px < x - 2 or px + bw > x + cols * bw:
                continue
            if idx in missing:
                idx += 1
                continue
            c.rect(px, py, bw, bh)
            idx += 1


def simple_shop(c, x, y):
    items = [("跳绳", "18元"), ("皮球", "26元"), ("画笔", "9元")]
    for i, (name, price) in enumerate(items):
        px = x + i * 90
        c.roundRect(px, y, 58, 42, 4)
        text(c, px + 8, y + 24, str(i + 1), 11, bold=True)
        text(c, px + 22, y + 24, name, 10)
        text(c, px + 17, y + 8, price, 10)


def draw_bus(c, x, y, label):
    c.roundRect(x, y, 74, 35, 5)
    c.rect(x + 8, y + 17, 18, 11)
    c.rect(x + 31, y + 17, 18, 11)
    c.circle(x + 16, y - 1, 5)
    c.circle(x + 58, y - 1, 5)
    text(c, x + 3, y - 20, label, 10)


def header(c, title, page_no, subtitle="一数 下（R）"):
    c.setStrokeColor(colors.grey)
    c.line(MARGIN_X + 28, PAGE_H - 42, PAGE_W - MARGIN_X - 28, PAGE_H - 42)
    centered(c, MARGIN_X, PAGE_H - 36, PAGE_W - 2 * MARGIN_X, title, 14)
    text(c, PAGE_W - MARGIN_X - 110, PAGE_H - 36, subtitle, 10)
    c.setStrokeColor(colors.black)
    c.setDash(1, 2)
    c.line(MARGIN_X - 14, MARGIN_Y + 10, MARGIN_X - 14, PAGE_H - MARGIN_Y)
    c.line(PAGE_W - MARGIN_X + 14, MARGIN_Y + 10, PAGE_W - MARGIN_X + 14, PAGE_H - MARGIN_Y)
    c.setDash()
    side_labels = [("姓名：", PAGE_H / 2 + 115), ("班级：", PAGE_H / 2), ("学号：", PAGE_H / 2 - 115)]
    for label, y in side_labels:
        x = MARGIN_X - 27
        c.setFont("Song", 7)
        c.saveState()
        c.translate(x, y)
        c.rotate(90)
        c.drawString(0, 0, label)
        c.restoreState()
        c.line(x + 5, y + 24, x + 5, y + 98)
    centered(c, 0, 17, PAGE_W, f"★ {page_no} ★", 9)


def section(c, x, y, title, score):
    text(c, x, y, title, 14, "Hei", True)
    text(c, x + 138, y + 1, f"（{score}）", 9)
    return y - 28


def page1(c):
    header(c, "一年级数学下册期末模拟真题卷", 1)
    y = TOP_Y - 44
    centered(c, LEFT_X, y, COL_W, "第一站：数的乐园", 13)
    y -= 32
    y = section(c, LEFT_X, y, "一、开动脑筋，我会填。", "每空1分，共25分")
    qs = [
        "1. 86 里面有（    ）个十和（    ）个一；与 86 相邻的两个数是（    ）和（    ）。",
        "2. 一个两位数，个位上是 7，十位上是 5，这个数写作（    ），读作（        ）。",
        "3. 比 40 多 9 的数是（    ）；68 比 70 少（    ）。",
        "4. 用 3 个十和 6 个一组成的数是（    ），再添上 4 个一是（    ）。",
        "5. 4 元 6 角 =（    ）角        72 角 =（    ）元（    ）角",
        "6. 9 角 + 5 元 =（    ）元（    ）角；8 元 - 3 元 5 角 =（    ）元（    ）角。",
    ]
    for q in qs:
        y = wrapped(c, LEFT_X, y, q, COL_W, 11, 24)
    text(c, LEFT_X, y, "7. 看图写数。写作：（      ）  读作：（              ）", 11)
    base_ten(c, LEFT_X + 118, y - 42, 4, 5, 1.1)
    y -= 72
    text(c, LEFT_X, y, "8. 根据百数表，在空格里填上合适的数。", 11)
    hundred_chart(c, LEFT_X + 74, y - 34, 64)
    hundred_chart(c, LEFT_X + 225, y - 34, 38)
    y -= 72
    text(c, LEFT_X, y, "9. 在下面数线上，箭头所指的数是（    ）；请标出 73 的位置。", 11)
    number_line(c, LEFT_X + 40, y - 38, 260, mark=30)
    y -= 70

    y = TOP_Y - 44
    centered(c, RIGHT_X, y, COL_W, "第二站：认真比较", 13)
    y -= 32
    y = section(c, RIGHT_X, y, "二、用心分析，我会选。", "每题2分，共12分")
    choices = [
        ("1. 小林买一本 24 元的故事书，付了 50 元，应找回（    ）元。", "① 24        ② 26        ③ 74"),
        ("2. 下面不能表示 35 - 20 的是（    ）。", "① 三捆十根和五根去掉两捆  ② 30 - 20 = 10, 10 + 5 = 15  ③ 35 - 2 = 33"),
        ("3. 一张正方形纸对折两次，可能折出的图形是（    ）。", "① 长方形        ② 圆        ③ 五边形"),
        ("4. 58 后面的第 3 个数是（    ）。", "① 59        ② 60        ③ 61"),
        ("5. 下面算式结果最接近 70 的是（    ）。", "① 40 + 28        ② 99 - 20        ③ 45 + 9"),
        ("6. 35 位于百数表中 34 的（    ）。", "① 左边        ② 右边        ③ 上面"),
    ]
    for q, ch in choices:
        y = wrapped(c, RIGHT_X, y, q, COL_W, 11, 20)
        text(c, RIGHT_X + 22, y, ch, 10)
        y -= 25
    y = section(c, RIGHT_X, y, "三、看清题目，我会算。", "共30分")
    text(c, RIGHT_X, y, "1. 口算。（12分）", 11)
    y -= 30
    rows = [
        ["17 + 8 =", "64 + 6 =", "52 - 7 =", "16 - 8 + 5 ="],
        ["36 - 9 =", "70 - 30 =", "48 + 20 =", "90 - 40 - 6 ="],
        ["58 + 7 =", "29 + 50 =", "74 - 28 =", "35 + 40 - 9 ="],
    ]
    for row in rows:
        for i, item in enumerate(row):
            text(c, RIGHT_X + i * 92, y, item, 11)
        y -= 29
    text(c, RIGHT_X, y, "2. 在 ○ 里填上“>”“<”或“=”。（8分）", 11)
    y -= 34
    comps = ["46 ○ 40+5", "63-8 ○ 55", "28+9 ○ 38", "72 ○ 80-9", "57+6 ○ 60", "91-30 ○ 62"]
    for i, item in enumerate(comps):
        text(c, RIGHT_X + (i % 3) * 120, y - (i // 3) * 28, item, 11)


def page2(c):
    header(c, "一年级数学下册期末模拟真题卷", 2)
    y = TOP_Y - 48
    text(c, LEFT_X, y, "3. 列竖式计算。（10分）", 12, "Hei", True)
    y -= 38
    for i, item in enumerate(["48 + 37 =", "83 - 46 =", "26 + 59 =", "92 - 38 ="]):
        text(c, LEFT_X + (i % 2) * 190, y - (i // 2) * 88, item, 12)
        c.line(LEFT_X + (i % 2) * 190, y - 48 - (i // 2) * 88, LEFT_X + (i % 2) * 190 + 90, y - 48 - (i // 2) * 88)
    y -= 185
    centered(c, LEFT_X, y, COL_W, "第三站：图形小屋", 13)
    y -= 34
    y = section(c, LEFT_X, y, "四、画一画，填一填。", "共10分")
    text(c, LEFT_X, y, "1. 下面这面墙缺了（    ）块砖。（3分）", 11)
    wall(c, LEFT_X + 85, y - 35)
    y -= 110
    text(c, LEFT_X, y, "2. 右边的图形中有（    ）个长方形，（    ）个三角形，", 11)
    text(c, LEFT_X + 20, y - 22, "（    ）个圆。（3分）", 11)
    x0, y0 = LEFT_X + 250, y - 45
    c.rect(x0, y0, 68, 35)
    path = c.beginPath()
    path.moveTo(x0 + 68, y0)
    path.lineTo(x0 + 100, y0 + 18)
    path.lineTo(x0 + 68, y0 + 35)
    path.close()
    c.drawPath(path)
    c.circle(x0 + 13, y0 - 9, 8)
    c.circle(x0 + 45, y0 - 9, 8)
    c.circle(x0 + 80, y0 - 9, 8)
    c.rect(x0 + 14, y0 + 10, 29, 15)
    y -= 95
    text(c, LEFT_X, y, "3. 按要求接着画。（4分）", 11)
    text(c, LEFT_X + 18, y - 32, "□ △ ○ □ △ ○ □ △ （    ） （    ）", 13)

    y = TOP_Y - 48
    centered(c, RIGHT_X, y, COL_W, "第四站：生活课堂", 13)
    y -= 34
    y = section(c, RIGHT_X, y, "五、解决问题。", "共30分")
    text(c, RIGHT_X, y, "1. 一年级去科技馆参观，车辆座位如下。", 11)
    draw_bus(c, RIGHT_X + 26, y - 62, "大客车 46 个座位")
    draw_bus(c, RIGHT_X + 150, y - 62, "中巴车 27 个座位")
    draw_bus(c, RIGHT_X + 275, y - 62, "小汽车 4 个座位")
    y -= 110
    text(c, RIGHT_X, y, "（1）一辆大客车和一辆中巴车一共有多少个座位？（3分）", 11)
    formula_boxes(c, RIGHT_X + 130, y - 38)
    y -= 78
    text(c, RIGHT_X, y, "（2）一（2）班有 49 人，坐满一辆中巴车后，还剩多少人？（3分）", 11)
    formula_boxes(c, RIGHT_X + 130, y - 38)
    y -= 78
    text(c, RIGHT_X, y, "2. 在文具店，亮亮和妈妈买东西。", 11)
    simple_shop(c, RIGHT_X + 45, y - 58)
    y -= 82
    text(c, RIGHT_X, y, "（1）买①号和③号，一共要多少元？（4分）", 11)
    formula_boxes(c, RIGHT_X + 125, y - 38)
    y -= 78
    text(c, RIGHT_X, y, "（2）带 50 元买②号和③号，够吗？在□里打“√”。（4分）", 11)
    formula_boxes(c, RIGHT_X + 125, y - 38)
    text(c, RIGHT_X + 80, y - 76, "够 □        不够 □", 11)


def page3(c):
    header(c, "一年级数学下册期末模拟真题卷", 3)
    y = TOP_Y - 48
    text(c, LEFT_X, y, "3. 看图列式计算。（8分）", 12, "Hei", True)
    y -= 42
    text(c, LEFT_X, y, "（1）", 11)
    c.line(LEFT_X + 58, y - 25, LEFT_X + 220, y - 25)
    c.line(LEFT_X + 58, y - 25, LEFT_X + 62, y - 20)
    c.line(LEFT_X + 220, y - 25, LEFT_X + 216, y - 20)
    text(c, LEFT_X + 112, y - 18, "80 本", 10)
    c.rect(LEFT_X + 70, y - 70, 62, 28)
    text(c, LEFT_X + 85, y - 61, "？本", 10)
    c.rect(LEFT_X + 150, y - 70, 62, 28)
    text(c, LEFT_X + 158, y - 61, "29 本", 10)
    formula_boxes(c, LEFT_X + 105, y - 110)
    y -= 155
    text(c, LEFT_X, y, "（2）", 11)
    base_ten(c, LEFT_X + 55, y - 42, 5, 6, 1.0)
    base_ten(c, LEFT_X + 200, y - 42, 2, 8, 1.0)
    text(c, LEFT_X + 104, y - 60, "比", 11)
    text(c, LEFT_X + 145, y - 60, "多？", 11)
    formula_boxes(c, LEFT_X + 105, y - 108)
    y -= 150
    text(c, LEFT_X, y, "4. 学校图书角原有 53 本绘本，借出 18 本，又还回 9 本。", 11)
    text(c, LEFT_X + 18, y - 25, "现在图书角有多少本绘本？（5分）", 11)
    formula_boxes(c, LEFT_X + 105, y - 70)
    y -= 112
    text(c, LEFT_X, y, "5. 把 43 颗纽扣装进盒子，每盒最多装 8 颗。", 11)
    text(c, LEFT_X + 18, y - 25, "可以装满几盒？还剩几颗？（5分）", 11)
    for i in range(43):
        c.circle(LEFT_X + 115 + (i % 16) * 11, y - 65 - (i // 16) * 12, 3)
    text(c, LEFT_X + 115, y - 120, "装满（    ）盒，还剩（    ）颗。", 11)

    y = TOP_Y - 48
    text(c, RIGHT_X, y, "6. 选择合适的条件（填序号），再解答。（5分）", 12, "Hei", True)
    y -= 36
    text(c, RIGHT_X, y, "美术社团一共有 38 人，（    ），女生有多少人？", 11)
    y -= 35
    c.roundRect(RIGHT_X + 15, y - 8, 330, 28, 4)
    text(c, RIGHT_X + 23, y, "① 男生有 17 人     ② 又来了 8 人     ③ 每组 6 人", 11)
    formula_boxes(c, RIGHT_X + 120, y - 58)
    y -= 105
    text(c, RIGHT_X, y, "7. 填表。（6分）", 12, "Hei", True)
    y -= 32
    data = [["物品", "足球", "跳棋", "水彩笔"], ["原有", "42个", "36副", "58盒"], ["卖出", "18个", "9副", "20盒"], ["还剩", "", "", ""]]
    cell_w, cell_h = 78, 28
    for r, row in enumerate(data):
        for col, val in enumerate(row):
            c.rect(RIGHT_X + col * cell_w, y - r * cell_h, cell_w, cell_h)
            centered(c, RIGHT_X + col * cell_w, y - r * cell_h + 8, cell_w, val, 10, "Song")
    y -= 145
    text(c, RIGHT_X, y, "8. 想一想，填一填。（6分）", 12, "Hei", True)
    y -= 32
    qs = [
        "（1）一个两位数，十位和个位上的数字和是 10，这个两位数最大是（    ）。",
        "（2）算式 64 - □，差的十位上还是 6，□ 里最大填（    ）。",
        "（3）算式 27 + □，和的个位是 2，□ 里最小填（    ）。",
    ]
    for q in qs:
        y = wrapped(c, RIGHT_X, y, q, COL_W, 11, 28)


def page4(c):
    header(c, "一年级数学下册期末模拟真题卷  参考答案", 4)
    y = TOP_Y - 52
    text(c, LEFT_X, y, "参考答案", 16, "Hei", True)
    y -= 34
    answers = [
        ("一、", "1. 8,6,85,87  2. 57,五十七  3. 49,2  4. 36,40  5. 46,7,2  6. 5,9,4,5  7. 45,四十五  8. 略  9. 30；略"),
        ("二、", "1.②  2.③  3.①  4.③  5.①  6.②"),
        ("三、", "1. 25,70,45,13；27,40,68,44；65,79,46,66  2. >,=,<,>,>,<  3. 85,37,85,54"),
        ("四、", "1. 3  2. 长方形2个，三角形1个，圆3个  3. ○、□"),
        ("五、", "1.(1)46+27=73(个) (2)49-27=22(人)  2.(1)18+9=27(元) (2)26+9=35(元)，够  3.(1)80-29=51(本) (2)56-28=28  4.53-18+9=44(本)  5.装满5盒，还剩3颗  6.选①，38-17=21(人)  7.24个，27副，38盒  8.(1)91 (2)4 (3)5"),
    ]
    for title, body in answers:
        text(c, LEFT_X, y, title, 12, "Hei", True)
        y = wrapped(c, LEFT_X + 35, y, body, PAGE_W - 2 * MARGIN_X - 35, 11, 23)
        y -= 10
    text(c, LEFT_X, y - 15, "说明：本卷为依据原 PDF 题型与一年级下册知识点重新编写的模拟卷，具体题目均为新题。", 10)


def page1_new(c):
    header(c, "一年级数学下册期末模拟真题卷", 1)
    y = TOP_Y - 44
    centered(c, LEFT_X, y, COL_W, "第一站：数的乐园", 13)
    y -= 32
    y = section(c, LEFT_X, y, "一、开动脑筋，我会填。", "每空1分，共25分")
    qs = [
        "1. 86 里面有（    ）个十和（    ）个一；与 86 相邻的两个数是（    ）和（    ）。",
        "2. 一个两位数，个位上是 7，十位上是 5，这个数写作（    ），读作（        ）。",
        "3. 比 40 多 9 的数是（    ）；68 比 70 少（    ）。",
        "4. 用 3 个十和 6 个一组成的数是（    ），再添上 4 个一是（    ）。",
        "5. 4 元 6 角 =（    ）角        72 角 =（    ）元（    ）角",
        "6. 9 角 + 5 元 =（    ）元（    ）角；8 元 - 3 元 5 角 =（    ）元（    ）角。",
    ]
    for q in qs:
        y = wrapped(c, LEFT_X, y, q, COL_W, 11, 24)
    text(c, LEFT_X, y, "7. 看图写数。写作：（      ）  读作：（              ）", 11)
    base_ten(c, LEFT_X + 118, y - 42, 4, 5, 1.1)
    y -= 78
    text(c, LEFT_X, y, "8. 根据百数表，在空格里填上合适的数。", 11)
    hundred_chart(c, LEFT_X + 74, y - 34, 64)
    hundred_chart(c, LEFT_X + 225, y - 34, 38)

    y = TOP_Y - 44
    centered(c, RIGHT_X, y, COL_W, "第二站：认真比较", 13)
    y -= 32
    y = section(c, RIGHT_X, y, "二、用心分析，我会选。", "每题2分，共12分")
    choices = [
        ("1. 小林买一本 24 元的故事书，付了 50 元，应找回（    ）元。", "① 24        ② 26        ③ 74"),
        ("2. 下面不能表示 35 - 20 的是（    ）。", "① 三捆十根和五根去掉两捆  ② 30 - 20 = 10, 10 + 5 = 15  ③ 35 - 2 = 33"),
        ("3. 一张正方形纸对折两次，可能折出的图形是（    ）。", "① 长方形        ② 圆        ③ 五边形"),
        ("4. 58 后面的第 3 个数是（    ）。", "① 59        ② 60        ③ 61"),
        ("5. 下面算式结果最接近 70 的是（    ）。", "① 40 + 28        ② 99 - 20        ③ 45 + 9"),
        ("6. 35 位于百数表中 34 的（    ）。", "① 左边        ② 右边        ③ 上面"),
    ]
    for q, ch in choices:
        y = wrapped(c, RIGHT_X, y, q, COL_W, 11, 21)
        text(c, RIGHT_X + 22, y, ch, 10)
        y -= 29


def page2_new(c):
    header(c, "一年级数学下册期末模拟真题卷", 2)
    y = TOP_Y - 48
    y = section(c, LEFT_X, y, "三、看清题目，我会算。", "共30分")
    text(c, LEFT_X, y, "1. 口算。（12分）", 11)
    y -= 30
    rows = [
        ["17 + 8 =", "64 + 6 =", "52 - 7 =", "16 - 8 + 5 ="],
        ["36 - 9 =", "70 - 30 =", "48 + 20 =", "90 - 40 - 6 ="],
        ["58 + 7 =", "29 + 50 =", "74 - 28 =", "35 + 40 - 9 ="],
    ]
    for row in rows:
        for i, item in enumerate(row):
            text(c, LEFT_X + i * 92, y, item, 11)
        y -= 30
    text(c, LEFT_X, y, "2. 在 ○ 里填上“>”“<”或“=”。（8分）", 11)
    y -= 34
    comps = ["46 ○ 40+5", "63-8 ○ 55", "28+9 ○ 38", "72 ○ 80-9", "57+6 ○ 60", "91-30 ○ 62"]
    for i, item in enumerate(comps):
        text(c, LEFT_X + (i % 3) * 122, y - (i // 3) * 28, item, 11)
    y -= 86
    text(c, LEFT_X, y, "3. 列竖式计算。（10分）", 12, "Hei", True)
    y -= 38
    for i, item in enumerate(["48 + 37 =", "83 - 46 =", "26 + 59 =", "92 - 38 ="]):
        px = LEFT_X + (i % 2) * 190
        py = y - (i // 2) * 82
        text(c, px, py, item, 12)
        c.line(px, py - 48, px + 90, py - 48)

    y = TOP_Y - 48
    centered(c, RIGHT_X, y, COL_W, "第三站：图形小屋", 13)
    y -= 34
    y = section(c, RIGHT_X, y, "四、画一画，填一填。", "共10分")
    text(c, RIGHT_X, y, "1. 下面这面墙缺了（    ）块砖。（3分）", 11)
    wall(c, RIGHT_X + 72, y - 35)
    y -= 110
    text(c, RIGHT_X, y, "2. 右边的图形中有（    ）个长方形，（    ）个三角形，", 11)
    text(c, RIGHT_X + 20, y - 22, "（    ）个圆。（3分）", 11)
    x0, y0 = RIGHT_X + 250, y - 45
    c.rect(x0, y0, 68, 35)
    path = c.beginPath()
    path.moveTo(x0 + 68, y0)
    path.lineTo(x0 + 100, y0 + 18)
    path.lineTo(x0 + 68, y0 + 35)
    path.close()
    c.drawPath(path)
    c.circle(x0 + 13, y0 - 9, 8)
    c.circle(x0 + 45, y0 - 9, 8)
    c.circle(x0 + 80, y0 - 9, 8)
    c.rect(x0 + 14, y0 + 10, 29, 15)
    y -= 95
    text(c, RIGHT_X, y, "3. 按要求接着画。（4分）", 11)
    text(c, RIGHT_X + 18, y - 32, "□ △ ○ □ △ ○ □ △ （    ） （    ）", 13)


def page3_new(c):
    header(c, "一年级数学下册期末模拟真题卷", 3)
    y = TOP_Y - 48
    centered(c, LEFT_X, y, COL_W, "第四站：生活课堂", 13)
    y -= 34
    y = section(c, LEFT_X, y, "五、解决问题。", "共30分")
    text(c, LEFT_X, y, "1. 一年级去科技馆参观，车辆座位如下。", 11)
    draw_bus(c, LEFT_X + 26, y - 62, "大客车 46 个座位")
    draw_bus(c, LEFT_X + 150, y - 62, "中巴车 27 个座位")
    draw_bus(c, LEFT_X + 275, y - 62, "小汽车 4 个座位")
    y -= 110
    text(c, LEFT_X, y, "（1）一辆大客车和一辆中巴车一共有多少个座位？（3分）", 11)
    formula_boxes(c, LEFT_X + 130, y - 38)
    y -= 78
    text(c, LEFT_X, y, "（2）一（2）班有 49 人，坐满一辆中巴车后，还剩多少人？（3分）", 11)
    formula_boxes(c, LEFT_X + 130, y - 38)
    y -= 78
    text(c, LEFT_X, y, "2. 在文具店，亮亮和妈妈买东西。", 11)
    simple_shop(c, LEFT_X + 45, y - 58)
    y -= 82
    text(c, LEFT_X, y, "（1）买①号和③号，一共要多少元？（4分）", 11)
    formula_boxes(c, LEFT_X + 125, y - 38)
    y -= 78

    y = TOP_Y - 48
    text(c, RIGHT_X, y, "3. 看图列式计算。（8分）", 12, "Hei", True)
    y -= 42
    text(c, RIGHT_X, y, "（1）", 11)
    c.line(RIGHT_X + 58, y - 25, RIGHT_X + 220, y - 25)
    c.line(RIGHT_X + 58, y - 25, RIGHT_X + 62, y - 20)
    c.line(RIGHT_X + 220, y - 25, RIGHT_X + 216, y - 20)
    text(c, RIGHT_X + 112, y - 18, "80 本", 10)
    c.rect(RIGHT_X + 70, y - 70, 62, 28)
    text(c, RIGHT_X + 85, y - 61, "？本", 10)
    c.rect(RIGHT_X + 150, y - 70, 62, 28)
    text(c, RIGHT_X + 158, y - 61, "29 本", 10)
    formula_boxes(c, RIGHT_X + 105, y - 110)
    y -= 155
    text(c, RIGHT_X, y, "（2）", 11)
    base_ten(c, RIGHT_X + 55, y - 42, 5, 6, 1.0)
    base_ten(c, RIGHT_X + 200, y - 42, 2, 8, 1.0)
    text(c, RIGHT_X + 104, y - 60, "比", 11)
    text(c, RIGHT_X + 145, y - 60, "多？", 11)
    formula_boxes(c, RIGHT_X + 105, y - 108)
    y -= 150
    text(c, RIGHT_X, y, "4. 学校图书角原有 53 本绘本，借出 18 本，又还回 9 本。", 11)
    text(c, RIGHT_X + 18, y - 25, "现在图书角有多少本绘本？（5分）", 11)
    formula_boxes(c, RIGHT_X + 105, y - 70)


def page4_new(c):
    header(c, "一年级数学下册期末模拟真题卷", 4)
    y = TOP_Y - 48
    text(c, LEFT_X, y, "2.（2）带 50 元买②号和③号，够吗？在□里打“√”。（4分）", 12, "Hei", True)
    formula_boxes(c, LEFT_X + 125, y - 42)
    text(c, LEFT_X + 80, y - 80, "够 □        不够 □", 11)
    y -= 128
    text(c, LEFT_X, y, "5. 把 43 颗纽扣装进盒子，每盒最多装 8 颗。", 12, "Hei", True)
    text(c, LEFT_X + 18, y - 28, "可以装满几盒？还剩几颗？（5分）", 11)
    for i in range(43):
        c.circle(LEFT_X + 105 + (i % 16) * 11, y - 72 - (i // 16) * 12, 3)
    text(c, LEFT_X + 95, y - 132, "装满（    ）盒，还剩（    ）颗。", 11)
    y -= 185
    text(c, LEFT_X, y, "6. 选择合适的条件（填序号），再解答。（5分）", 12, "Hei", True)
    y -= 36
    text(c, LEFT_X, y, "美术社团一共有 38 人，（    ），女生有多少人？", 11)
    y -= 35
    c.roundRect(LEFT_X + 15, y - 8, 330, 28, 4)
    text(c, LEFT_X + 23, y, "① 男生有 17 人     ② 又来了 8 人     ③ 每组 6 人", 11)
    formula_boxes(c, LEFT_X + 120, y - 58)

    y = TOP_Y - 48
    text(c, RIGHT_X, y, "7. 填表。（6分）", 12, "Hei", True)
    y -= 32
    data = [["物品", "足球", "跳棋", "水彩笔"], ["原有", "42个", "36副", "58盒"], ["卖出", "18个", "9副", "20盒"], ["还剩", "", "", ""]]
    cell_w, cell_h = 78, 28
    for r, row in enumerate(data):
        for col, val in enumerate(row):
            c.rect(RIGHT_X + col * cell_w, y - r * cell_h, cell_w, cell_h)
            centered(c, RIGHT_X + col * cell_w, y - r * cell_h + 8, cell_w, val, 10, "Song")
    y -= 145
    text(c, RIGHT_X, y, "8. 想一想，填一填。（6分）", 12, "Hei", True)
    y -= 32
    qs = [
        "（1）一个两位数，十位和个位上的数字和是 10，这个两位数最大是（    ）。",
        "（2）算式 64 - □，差的十位上还是 6，□ 里最大填（    ）。",
        "（3）算式 27 + □，和的个位是 2，□ 里最小填（    ）。",
    ]
    for q in qs:
        y = wrapped(c, RIGHT_X, y, q, COL_W, 11, 34)


def page5_answers(c):
    header(c, "一年级数学下册期末模拟真题卷  参考答案", 5)
    y = TOP_Y - 52
    text(c, LEFT_X, y, "参考答案", 16, "Hei", True)
    y -= 34
    answers = [
        ("一、", "1. 8,6,85,87  2. 57,五十七  3. 49,2  4. 36,40  5. 46,7,2  6. 5,9,4,5  7. 45,四十五  8. 略"),
        ("二、", "1.②  2.③  3.①  4.③  5.①  6.②"),
        ("三、", "1. 25,70,45,13；27,40,68,44；65,79,46,66  2. >,=,<,>,>,<  3. 85,37,85,54"),
        ("四、", "1. 3  2. 长方形2个，三角形1个，圆3个  3. ○、□"),
        ("五、", "1.(1)46+27=73(个) (2)49-27=22(人)  2.(1)18+9=27(元) (2)26+9=35(元)，够  3.(1)80-29=51(本) (2)56-28=28  4.53-18+9=44(本)  5.装满5盒，还剩3颗  6.选①，38-17=21(人)  7.24个，27副，38盒  8.(1)91 (2)4 (3)5"),
    ]
    for title, body in answers:
        text(c, LEFT_X, y, title, 12, "Hei", True)
        y = wrapped(c, LEFT_X + 35, y, body, PAGE_W - 2 * MARGIN_X - 35, 11, 23)
        y -= 10
    text(c, LEFT_X, y - 15, "说明：本卷为依据原 PDF 题型与一年级下册知识点重新编写的模拟卷，具体题目均为新题。", 10)


def main():
    setup_fonts()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT_FILE), pagesize=landscape(A4))
    for draw in (page1_new, page2_new, page3_new, page4_new, page5_answers):
        draw(c)
        c.showPage()
    c.save()
    print(OUT_FILE)


if __name__ == "__main__":
    main()
