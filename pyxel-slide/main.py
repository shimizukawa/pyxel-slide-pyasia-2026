# author: Takayuki Shimizukawa
# license: MIT
# version: 1.0
#
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "markdown-it-py",
#     "linkify-it-py",
#     "pygments",
#     "pyxel",
# ]
# ///
from __future__ import annotations

import asyncio
import contextlib
import dataclasses
import enum
import itertools
import re
import sys
import webbrowser
from pathlib import Path
from random import randint, choice

import pyxel


MD_FILENAME = "slide-en.md"
# DEBUG = True
DEBUG = False

LINE_NUMS = 12  # lines per page
LINE_MARGIN_RATIO = 0.5  # 50% of font height (between paragraphs)
LINE_MARGIN_RATIO_WRAP = 0.25  # 25% of font height (on line wrap)
DEFAULT_LINE_HEIGHT = int(12 * (1 + LINE_MARGIN_RATIO))  # default font height 12
WINDOW_PADDING = DEFAULT_LINE_HEIGHT // 2
HEIGHT = DEFAULT_LINE_HEIGHT * LINE_NUMS
WIDTH = HEIGHT * 16 // 9
FPS = 30
KEY_REPEAT = 1  # for 30fps
KEY_HOLD = 15  # for 30fps
print(f"{WIDTH=}, {HEIGHT=}")
FONT_MAP = {
    "title": "assets/b24_b.bdf",
    "pagetitle": "assets/b16_b.bdf",
    "default": "assets/b12.bdf",
    "strong": "assets/b12_b.bdf",
    "em": "assets/b12_i.bdf",
    "literal": "assets/b12.bdf",
}
LIST_MARKERS = ["unused", "●", "○", "■", "▲", "▼", "★"]

DIRECTION_MAP = {
    ("f", "h2"): "right",
    ("f", "h3"): "down",
    ("b", "h3"): "up",
    ("b", "h2"): "left",
}

HUMAN_IMAGES = [
    (368, 8, 16, 16),
    (368, 56, 16, 16),
    (368, 104, 16, 16),
    (368, 152, 16, 16),
    (368, 200, 16, 16),
    (368, 248, 16, 16),
]

directive_pattern = re.compile(r"^{(.+?)}\s*(.*)$")
directive_option_pattern = re.compile(r":(\w+): (.+)", re.MULTILINE)


@dataclasses.dataclass
class Slide:
    path: Path
    sec: int
    page: int
    tokens: list
    level: str


def get_slide_title(slide: Slide) -> str:
    for token in slide.tokens:
        if token.type == "heading_open" and token.tag in ("h1", "h2"):
            title_token = next(
                (t for t in slide.tokens if t.type == "inline" and t.map == token.map),
                None,
            )
            if title_token:
                if title_token.children:
                    title = "".join(
                        tok.content for tok in title_token.children if tok.type == "text"
                    )
                else:
                    title = title_token.content
                return title
    raise ValueError("No title found in the slide.")


class NavBtn:
    DOWN = 0
    LEFT = 1
    UP = 2
    RIGHT = 3
    NEXT = 4
    PREV = 6

    def __init__(self, i, offset_x, offset_y, col, active_col, on):
        self.i = i
        self.col = col
        self.active_col = active_col
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.setup_coords(i)
        self.on = on
        self.hover = False

    def setup_coords(self, i):
        c = 45 * (1 + i * 2)
        sin = pyxel.sin
        cos = pyxel.cos
        xlist = []
        ylist = []
        for x1, y1, x2, y2 in ((9, 9, 2, 9), (9, 9, 9, 2)):
            # Calculate line coordinates rotated 45 degrees around the origin
            rx1 = round(x1 * cos(c) - y1 * sin(c))
            ry1 = round(x1 * sin(c) + y1 * cos(c))
            rx2 = round(x2 * cos(c) - y2 * sin(c))
            ry2 = round(x2 * sin(c) + y2 * cos(c))
            xlist.append((rx1, rx2))
            ylist.append((ry1, ry2))

        if i == self.NEXT:
            # Shorten the DOWN vertical and place it closer to center
            ylist[0] = (ylist[0][0] - 9, ylist[0][1] - 6)
            ylist[1] = (ylist[1][0] - 9, ylist[1][1] - 6)
        elif i == self.PREV:
            # Shorten the UP vertical and place it closer to center
            ylist[0] = (ylist[0][0] + 9, ylist[0][1] + 6)
            ylist[1] = (ylist[1][0] + 9, ylist[1][1] + 6)

        self.xlist = xlist
        self.ylist = ylist
        xflat = list(itertools.chain(*xlist))
        yflat = list(itertools.chain(*ylist))
        self.rect = (min(xflat), min(yflat), max(xflat), max(yflat))

    def update(self):
        # mouse
        self.hover = (
            self.rect[0] <= pyxel.mouse_x - self.offset_x <= self.rect[2]
            and self.rect[1] <= pyxel.mouse_y - self.offset_y <= self.rect[3]
        )

        # action
        if (
            self.i == self.DOWN
            and (
                pyxel.btnp(pyxel.KEY_DOWN, KEY_HOLD, KEY_REPEAT)
                or pyxel.btnp(pyxel.KEY_J, KEY_HOLD, KEY_REPEAT)
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)
            )
            or self.i == self.LEFT
            and (
                pyxel.btnp(pyxel.KEY_LEFT, KEY_HOLD, KEY_REPEAT)
                or pyxel.btnp(pyxel.KEY_H, KEY_HOLD, KEY_REPEAT)
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
            )
            or self.i == self.UP
            and (
                pyxel.btnp(pyxel.KEY_UP, KEY_HOLD, KEY_REPEAT)
                or pyxel.btnp(pyxel.KEY_K, KEY_HOLD, KEY_REPEAT)
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP)
            )
            or self.i == self.RIGHT
            and (
                pyxel.btnp(pyxel.KEY_RIGHT, KEY_HOLD, KEY_REPEAT)
                or pyxel.btnp(pyxel.KEY_L, KEY_HOLD, KEY_REPEAT)
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
            )
            or self.i == self.NEXT
            and (
                (
                    pyxel.btnp(pyxel.KEY_SPACE, KEY_HOLD, KEY_REPEAT)
                    and not pyxel.btn(pyxel.KEY_SHIFT)
                )
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
            )
            or self.i == self.PREV
            and (
                (
                    pyxel.btnp(pyxel.KEY_SPACE, KEY_HOLD, KEY_REPEAT)
                    and pyxel.btn(pyxel.KEY_SHIFT)
                )
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)
            )
            or self.hover
            and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
        ):
            self.on()
            self.hover = True

    def draw(self):
        ox = self.offset_x
        oy = self.offset_y
        col = self.active_col if self.hover else self.col

        for (x1, x2), (y1, y2) in zip(self.xlist, self.ylist):
            pyxel.line(ox + x1, oy + y1, ox + x2, oy + y2, col)


class FontLoader:
    def __init__(self, font_map):
        self._font_cache = {}
        self.is_init = False
        self._init_process = None
        self.fonts = {}
        self.font_map = font_map

    def _load_font(self):
        for key, fn in self.font_map.items():
            if fn not in self._font_cache:
                font = pyxel.Font(fn)
                self._font_cache[fn] = font
            self.fonts[key] = self._font_cache[fn]
            yield

    def init_processing(self) -> bool:
        """return True if it is still processing"""
        print("init_processing")
        if self.is_init:
            return False
        if self._init_process is None:
            self._init_process = self._load_font()
        try:
            next(self._init_process)
            return True
        except StopIteration:
            self.is_init = True
            return False

    def __getitem__(self, key):
        return self.fonts[key]

    @property
    def default(self) -> pyxel.Font | None:
        if "default" in self.fonts:
            return self.fonts["default"]
        elif self.fonts:
            return list(self.fonts.values())[0]
        return None

    @property
    def choiced(self) -> pyxel.Font | None:
        if self.fonts:
            return choice(list(self.fonts.values()))
        return None


class Paging:
    class Mode(enum.IntEnum):
        DITHER = enum.auto()
        NONE = enum.auto()
        NONE_SLOW = enum.auto()
        DITHER_SLOW = enum.auto()

    def __init__(self, mode = Mode.DITHER):
        self._changed_frame = -100
        self.mode = mode

    @property
    def is_dither(self):
        return self.mode in (self.Mode.DITHER, self.Mode.DITHER_SLOW)

    @property
    def is_slow(self):
        return self.mode in (self.Mode.DITHER_SLOW, self.Mode.NONE_SLOW)

    @property
    def delta(self) -> float:
        return (1 if self.is_slow else 3) / FPS

    def rotate(self):
        ml = list(self.Mode)
        idx = (ml.index(self.mode) + 1) % len(ml)
        self.mode = ml[idx]
        self._changed_frame = pyxel.frame_count

    def draw(self, font: pyxel.Font | None = None):
        if self._changed_frame + 60 > pyxel.frame_count:
            pyxel.text(0, 0, f"Paging Mode: {self.mode.name}", 0, font)


class ChildAppProxy:

    def __init__(
        self,
        filename: str,
        x: int,
        y: int,
        w: int,
        h: int,
        s: float | None,
    ):
        dotted_module = filename.replace("/", ".").replace("\\", ".").replace(".py", "")
        mod = __import__(dotted_module)
        for attr in dotted_module.split(".")[1:]:
            mod = getattr(mod, attr)

        # Handle scale
        if s is not None:
            w = int(w / s)
            h = int(h / s)
        self.app = mod.App(w, h)
        self.scale = s = s or 1.0
        # x coordinate: only left padding is considered
        self.x = max((pyxel.width - w * s) // 2, WINDOW_PADDING)
        self.y = y
        self.colors = list(pyxel.colors)  # Backup colors for child app

    def blt(self):
        a = self.app
        pyxel.colors[:] = self.colors  # Switch to child app colors
        g = a.render()
        x = max((pyxel.width - g.width) // 2, WINDOW_PADDING)
        x = WINDOW_PADDING + self.x
        y = WINDOW_PADDING + self.y
        s1 = self.scale or 1
        s2 = (1 - s1) / 2
        w, h = g.width, g.height
        pyxel.blt(x - int(w * s2), y - int(h * s2), g, 0, 0, w, h, scale=self.scale)
        if self.is_active:
            pyxel.rectb(x, y, int(w * s1), int(h * s1), 8)

    def unload(self):
        sys.modules.pop(self.app.__module__, None)

    @property
    def is_active(self):
        a = self.app
        if (self.x <= pyxel.mouse_x - WINDOW_PADDING < self.scale * a.width + self.x) and (
            self.y <= pyxel.mouse_y - WINDOW_PADDING < self.scale * a.height + self.y
        ):
            return True
        return False
    
    def update(self):
        self.app.update()


class App:
    def __init__(self):
        self.slides = self.load_slides(MD_FILENAME)
        if not self.slides:
            raise ValueError("No slides found in the markdown file.")
        title = get_slide_title(self.slides[0])
        pyxel.init(
            WIDTH + WINDOW_PADDING * 2,
            HEIGHT + WINDOW_PADDING,
            title=title,
            fps=FPS,
            quit_key=pyxel.KEY_NONE,
            display_scale=1,
        )
        self.colors = list(pyxel.colors)  # Backup colors for the parent app
        self._page = 0
        self.child_apps = {}
        nav_x, nav_y = pyxel.width - 20, pyxel.height - 20
        self.navs = [
            NavBtn(NavBtn.DOWN, nav_x, nav_y, 5, 9, self.go_next_page),
            NavBtn(NavBtn.LEFT, nav_x, nav_y, 5, 9, self.go_prev_section),
            NavBtn(NavBtn.UP, nav_x, nav_y, 5, 9, self.go_prev_page),
            NavBtn(NavBtn.RIGHT, nav_x, nav_y, 5, 9, self.go_next_section),
            NavBtn(NavBtn.NEXT, nav_x, nav_y, 5, 9, self.go_forward),
            NavBtn(NavBtn.PREV, nav_x, nav_y, 5, 9, self.go_backward),
        ]
        pyxel.mouse(True)
        self.reset()
        self.fonts = FontLoader(FONT_MAP)

        # run forever
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.renderd_page_bank = [
            (None, pyxel.Image(WIDTH, HEIGHT)),
            (None, pyxel.Image(WIDTH, HEIGHT)),
        ]
        self.first_pages_in_section = []  # First page index of each section
        self.slides = self.load_slides(MD_FILENAME)
        for i, slide in enumerate(self.slides):
            if slide.level in ("h1", "h2"):
                self.first_pages_in_section.append(i)
        self._page = min(self.page, len(self.slides) - 1)  # In case the page count decreased
        self.in_transition = [0, 0, "down"]  # (rate(1..0), old_page, direction)
        for app in self.child_apps.values():
            app.unload()
        self.child_apps = {}  # key: page index, value: child app
        self.child_is_updated = False
        self.links = {}  # key: page index, value: list of (x1, y1, x2, y2, url)
        self.paging = Paging()

        # player
        self.player_image = pyxel.Image.from_image("assets/urban_rpg.png")
        # Place at position based on current page
        x = WIDTH * self.page // max(1, len(self.slides) - 1)
        y = pyxel.height - 16
        self.player = (x, y, 1, 0)  # (x, y, u, v) - facing down, idle

    def load_slides(self, filepath) -> list[Slide]:
        import markdown_it

        md = markdown_it.MarkdownIt("gfm-like")
        path = Path(filepath).resolve().parent
        content = Path(filepath).read_text(encoding="utf-8")
        tokens = md.parse(content)
        slides: list[Slide] = []
        slide_tokens: list[markdown_it.token.Token] = []
        sec = 0
        page = 0
        for token in tokens:
            if token.type == "heading_open" and token.tag in ["h1", "h2", "h3"]:
                if slide_tokens:
                    slides.append(
                        Slide(path, sec, page, slide_tokens, slide_tokens[0].tag)
                    )
                    page += 1
                    sec = sec + 1 if token.tag in ("h1", "h2") else sec
                    slide_tokens = []
            slide_tokens.append(token)
        if slide_tokens:
            slides.append(Slide(path, sec, page, slide_tokens, slide_tokens[0].tag))

        return slides

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, new_page):
        old_page, self._page = self._page, new_page
        if old_page != new_page:
            self.render_page(new_page)

        if old_page < new_page:  # forward
            self.in_transition = [
                1.0,
                old_page,
                DIRECTION_MAP["f", self.slides[new_page].level],
            ]
        if old_page > new_page:  # backward
            self.in_transition = [
                1.0,
                old_page,
                DIRECTION_MAP["b", self.slides[old_page].level],
            ]

    def go_forward(self):
        self.page = min((self.page + 1), len(self.slides) - 1)

    def go_backward(self):
        self.page = max((self.page - 1), 0)

    def go_next_page(self):
        if (
            self.page + 1 not in self.first_pages_in_section
            and self.page != len(self.slides) - 1
        ):
            self.page += 1

    def go_prev_page(self):
        if self.page not in self.first_pages_in_section:
            self.page -= 1

    def go_next_section(self):
        sec = min(self.slides[self.page].sec + 1, len(self.first_pages_in_section) - 1)
        self.page = self.first_pages_in_section[sec]

    def go_prev_section(self):
        sec = max(self.slides[self.page].sec - 1, 0)
        self.page = self.first_pages_in_section[sec]

    def update_child(self):
        """Update the child app.

        Conditions to update:
        - Currently showing a page that has a child app
        - Not in a transition
        - Mouse is inside the child app area
        """
        if self.page not in self.child_apps:
            return False
        if self.in_transition[0] > 0:
            return False

        a = self.child_apps[self.page]
        if a.is_active:
            a.update()
            return True

        return False

    def update(self):
        self.child_is_updated = self.update_child()
        if self.child_is_updated:
            return

        if pyxel.btnp(pyxel.KEY_Q) and pyxel.btn(pyxel.KEY_CTRL):
            pyxel.quit()

        if pyxel.btnp(pyxel.KEY_R) and pyxel.btn(pyxel.KEY_CTRL):
            self.reset()

        if pyxel.btnp(pyxel.KEY_1):
            self.paging.rotate()

        if self.in_transition[0] > 0:
            self.in_transition[0] = self.in_transition[0] - self.paging.delta

        # Check for link clicks
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.in_transition[0] <= 0:
            self.check_link_click()

        for nav in self.navs:
            nav.update()

        self.update_player()

    def check_link_click(self):
        """Open a link in the browser if the mouse is inside a link area."""
        if self.page not in self.links:
            return

        mx = pyxel.mouse_x - WINDOW_PADDING
        my = pyxel.mouse_y - WINDOW_PADDING
        for x1, y1, x2, y2, url in self.links[self.page]:
            if x1 <= mx <= x2 and y1 <= my <= y2:
                webbrowser.open(url)
                return

    def update_player(self):
        # Auto-walk player based on slide progress
        x, y, u, v = self.player
        
        # Y is always fixed at the bottom
        y = pyxel.height - 16
        
        # Do not move if there is only one slide
        if len(self.slides) <= 1:
            self.player = (x, y, 1, 0)  # facing down, idle
            return
        
        # Calculate the target X position based on the current page
        target_x = WIDTH * self.page // (len(self.slides) - 1)
        
        # Move toward the target position
        diff = target_x - x
        
        if abs(diff) >= 1:
            # Run if distance is 32px or more (2 character widths)
            if abs(diff) >= 32:
                speed = 2  # Double movement speed
                anim_div = 2  # Double animation speed
            else:
                speed = 1  # Normal walk speed
                anim_div = 5  # Normal animation speed
            
            # Move
            if diff > 0:
                dx = speed
                u, v = 3, 1  # Facing right, ready to walk
            else:
                dx = -speed
                u, v = 0, 1  # Facing left, ready to walk
            
            # Walk/run animation
            v += [-1, 0, -1, 1][pyxel.frame_count // anim_div % 4]
            x += dx
        else:
            # Stopped: facing down, idle
            u, v = 1, 0
        
        self.player = (x, y, u, v)

    def draw_players(self, players):
        players = sorted(players, key=lambda o: o["player"][1])
        for obj in players:
            x, y, u, v = obj["player"]
            if idx := obj["id"]:
                idx = sum(obj["id"].encode("utf8")) % (len(HUMAN_IMAGES) - 1) + 1
            image = HUMAN_IMAGES[idx]

            pyxel.blt(
                x,
                y - 1,
                self.player_image,
                image[0] + u * 16,
                image[1] + v * 16,
                image[2],
                image[3],
                8,
            )

    def blt_player(self):
        # Draw players
        self.draw_players([{"player": self.player, "id": 0 }])
    
    def draw_loading(self):
        self.blt_player()
        # use default font to show if loaded, otherwise pyxel's built-in font
        msg = "NOW LOADING"
        font = self.fonts.choiced
        if font:
            msg_width = font.text_width(msg)  # Assuming each character is 8 pixels wide
        else:
            msg_width = len(msg) * 8  # Assuming each character is 8 pixels wide
        x = (WIDTH - msg_width) // 2 + randint(-50, 50)
        y = HEIGHT // 2 + randint(-30, 30)
        pyxel.text(x, y, msg, randint(0, 6), font)
        self.fonts.init_processing()

    def draw(self):
        pyxel.cls(7)
        if not self.fonts.is_init:
            self.draw_loading()
            return

        self.blt_slide()
        # Draw child app
        self.blt_child()
        self.blt_player()
        # Navigation
        self.draw_nav()
        # Display Paging Mode
        self.paging.draw(self.fonts.default)

    def render_page(self, page: int) -> pyxel.Image:
        """render page to old image bank"""
        for p, img in self.renderd_page_bank:
            if p == page:
                return img

        _, img = self.renderd_page_bank.pop(0)
        img.rect(0, 0, WIDTH, HEIGHT, 7)
        visitor = Visitor(self, page, img)
        visitor.walk(self.slides[page].tokens)
        self.renderd_page_bank.append((page, img))
        return img

    def get_rendered_img(self, page: int):
        for i, (p, img) in enumerate(self.renderd_page_bank):
            if p == page:
                used = self.renderd_page_bank.pop(i)
                self.renderd_page_bank.append(used)
                return img
        else:
            return self.render_page(page)

    def blt_slide(self):
        if self.in_transition[0] > 0:
            rate, old_page, direction = self.in_transition
            if direction == "down":
                old_x = WINDOW_PADDING
                old_y = WINDOW_PADDING - HEIGHT * (1 - rate) ** 2
                new_x = WINDOW_PADDING
                new_y = WINDOW_PADDING + HEIGHT * rate**2
            elif direction == "up":
                old_x = WINDOW_PADDING
                old_y = WINDOW_PADDING + HEIGHT * (1 - rate) ** 2
                new_x = WINDOW_PADDING
                new_y = WINDOW_PADDING - HEIGHT * rate**2
            elif direction == "right":
                old_x = WINDOW_PADDING - WIDTH * (1 - rate) ** 2
                old_y = WINDOW_PADDING
                new_x = WINDOW_PADDING + WIDTH * rate**2
                new_y = WINDOW_PADDING
            elif direction == "left":
                old_x = WINDOW_PADDING + WIDTH * (1 - rate) ** 2
                old_y = WINDOW_PADDING
                new_x = WINDOW_PADDING - WIDTH * rate**2
                new_y = WINDOW_PADDING
            new_img = self.get_rendered_img(self.page)
            old_img = self.get_rendered_img(old_page)
            # old
            if self.paging.is_dither:
                pyxel.dither(rate)
            pyxel.blt(old_x, old_y, old_img, 0, 0, WIDTH, HEIGHT, 7)
            # new
            if self.paging.is_dither:
                pyxel.dither(1 - rate)
            pyxel.blt(new_x, new_y, new_img, 0, 0, WIDTH, HEIGHT, 7)
            pyxel.dither(1)
        else:
            img = self.get_rendered_img(self.page)
            pyxel.blt(WINDOW_PADDING, WINDOW_PADDING, img, 0, 0, WIDTH, HEIGHT)
            if self.child_is_updated:
                pyxel.dither(0.5)
                pyxel.rect(0, 0, pyxel.width, pyxel.height, 13)
                pyxel.dither(1.0)

    def blt_child(self):
        """Overlay the child app onto the slide."""
        if self.page not in self.child_apps:
            pyxel.colors[:] = self.colors  # Restore colors for the parent app
            return
        if self.in_transition[0] > 0:
            return

        a = self.child_apps[self.page]
        a.blt()

    def draw_nav(self):
        if self.child_is_updated:
            return
        if (
            self.page + 1 not in self.first_pages_in_section
            and self.page != len(self.slides) - 1
        ):
            # Not the last page in the section
            self.navs[NavBtn.DOWN].draw()  # ↓
        if self.page < self.first_pages_in_section[-1]:
            # Not the last section
            self.navs[NavBtn.RIGHT].draw()  # →
        if self.page not in self.first_pages_in_section:
            # Not the first page in the section
            self.navs[NavBtn.UP].draw()  # ↑
        if self.page != 0:
            # Not the first section
            self.navs[NavBtn.LEFT].draw()  # ←
        if self.page < len(self.slides) - 1:
            # Not the last page
            self.navs[NavBtn.NEXT].draw()  # SPACE
        # self.navs[NavBtn.PREV].draw() # SHIFT+SPACE is not drawn


def use_font(font: str):
    def decorator(func):
        def wrapper(self, token):
            self.font_stack.append(font)
            func(self, token)
            self.font_stack.pop()

        return wrapper

    return decorator


def use_color(fg: int, bg: int):
    def decorator(func):
        def wrapper(self, token):
            self.color_stack.append((fg, bg))
            func(self, token)
            self.color_stack.pop()

        return wrapper

    return decorator


@contextlib.contextmanager
def with_color(self, fg: int, bg: int):
    self.color_stack.append((fg, bg))
    yield
    self.color_stack.pop()


class Visitor:
    list_stack: list[tuple[str, int]]
    color_stack: list[tuple[int, int]]

    def __init__(self, app: App, page: int, img: pyxel.Image):
        self.app = app
        self.img = img
        self.page = page
        self.x = 0
        self.y = 0
        self.used_width = 0
        self.indent_stack = [self.x]
        self.font_stack = ["default"]
        self.color_stack = [(0, -1)]  # fg, bg
        self.section_level = 0
        self.align = "left"
        self.list_stack = []  # For list markers (bullet/ordered)
        self.current_link = None  # リンク情報: {"x": x, "y": y, "url": url}
        self.app.links[page] = []

    @property
    def color(self):
        return self.color_stack[-1][0]

    @property
    def bgcolor(self):
        return self.color_stack[-1][1]

    @property
    def font(self):
        return self.app.fonts[self.font_stack[-1]]

    @property
    def font_height(self):
        return self.font.text_width("あ")  # Use the width of "あ" as the font height

    @property
    def list_marker(self):
        list_level = len(self.list_stack)
        list_type, ordered_num = self.list_stack[-1]
        if list_type == "ordered":
            return f"{ordered_num}. "
        elif list_type == "bullet":
            return LIST_MARKERS[list_level]  # 深いとエラーになるけど実質問題ない

    def _text(self, text):
        w = self.font.text_width(text)
        # Alignment
        if self.align == "center":
            self.x = (WIDTH - w) // 2
        elif self.align == "right":
            self.x = WIDTH - w

        # Background color
        if self.bgcolor >= 0:
            self.img.rect(self.x, self.y, w, self.font_height, self.bgcolor)

        if DEBUG:
            self.img.rectb(self.x, self.y, w, self.font_height, 0)

        self.img.text(self.x, self.y, text, self.color, self.font)

        # Bug: position shifts when _text is called consecutively with center or right alignment
        self.x += w

    def _crlf(self, margin: bool = False, wrap_margin: bool = False):
        # carriage return
        self.x = self.indent_stack[-1]
        self.used_width = self.x
        # line feed
        self.y += self.font_height
        if margin:
            # Add 50% of font height as margin (between paragraphs)
            self.y += int(self.font_height * LINE_MARGIN_RATIO)
        elif wrap_margin:
            # Add 25% of font height as margin (on line wrap)
            self.y += int(self.font_height * LINE_MARGIN_RATIO_WRAP)

    def _indent(self, indent):
        self.x += indent
        self.indent_stack.append(self.x)

    def _dedent(self):
        dedent = self.indent_stack.pop() - self.indent_stack[-1]
        self.x -= dedent

    def walk(self, tokens):
        for token in tokens:
            self.visit(token)
            if token.children:
                self.walk(token.children)
            self.depart(token)

    def visit(self, token):
        method_name = f"visit_{token.type}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            method(token)
        else:
            print("visit", token.type)

    def depart(self, token):
        method_name = f"depart_{token.type}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            method(token)

    def visit_heading_open(self, token):
        if token.tag == "h1":
            self.section_level = 1
            self.font_stack.append("title")
            self.align = "center"
            self._crlf()
        elif token.tag == "h2":
            self.section_level = 2
            self.font_stack.append("title")
            self.align = "center"
            self._crlf()
            self._crlf()
        elif token.tag == "h3":
            self.section_level = 3
            self.font_stack.append("pagetitle")
            self.align = "left"
            self._text("# ")

    def visit_heading_close(self, token):
        self._crlf()
        self._crlf()
        self.font_stack.pop()

    def visit_text(self, token):
        content = token.content
        while content:
            i = len(content)
            w = self.font.text_width(content)
            while w + self.used_width > WIDTH:
                i -= 1
                w = self.font.text_width(content[:i])
            if DEBUG:
                self.img.rectb(self.x, self.y, w, self.font_height, 2)
                print(f"{self.used_width=}, {self.x=}, {w=}, {content[:i]}")
            self.used_width += w
            self._text(content[:i])
            content = content[i:]
            if content:
                self._crlf(wrap_margin=True)

    def visit_bullet_list_open(self, token):
        self._indent(WINDOW_PADDING)
        self.list_stack.append(("bullet", 1))

    def visit_bullet_list_close(self, token):
        self._dedent()
        self.list_stack.pop()
        self.y += self.font_height // 4
        # if not self.list_stack:
        #     self.y += self.font_height // 2

    def visit_ordered_list_open(self, token):
        self._indent(WINDOW_PADDING)
        self.list_stack.append(("ordered", 1))

    def visit_ordered_list_close(self, token):
        self._dedent()
        self.list_stack.pop()
        self.y += self.font_height // 4
        # if not self.list_stack:
        #     self.y += self.font_height // 2

    def visit_list_item_open(self, token):
        x = self.x
        self._text(self.list_marker)  # Ideally this should use a negative indent
        self.x = x  # Restore the original x position
        w = self.font.text_width(self.list_marker)
        self.used_width += w
        self._indent(max(self.font_height, w))

    def visit_list_item_close(self, token):
        self._dedent()
        list_type, ordered_num = self.list_stack.pop()
        self.list_stack.append((list_type, ordered_num + 1))

    def visit_paragraph_open(self, token):
        pass

    def visit_paragraph_close(self, token):
        self._crlf(margin=True)

    def visit_em_open(self, token):
        self.color_stack.append((9, -1))
        self.font_stack.append("em")

    def visit_em_close(self, token):
        self.font_stack.pop()
        self.color_stack.pop()

    def visit_strong_open(self, token):
        self.color_stack.append((4, -1))
        self.font_stack.append("strong")

    def visit_strong_close(self, token):
        self.font_stack.pop()
        self.color_stack.pop()

    def visit_inline(self, token):
        pass

    def visit_link_open(self, token):
        url = token.attrs.get("href", "")
        self.current_link = {"x": self.x, "y": self.y, "url": url}
        self.color_stack.append((5, -1))

    def visit_link_close(self, token):
        self.color_stack.pop()
        if self.current_link:
            x, y = self.current_link["x"], self.current_link["y"]
            url = self.current_link["url"]
            self.img.line(x, y + self.font_height, self.x, y + self.font_height, 5)
            # Register the link area
            if url:
                self.app.links[self.page].append((x, y, self.x, y + self.font_height, url))
            self.current_link = None

    @use_font("literal")
    @use_color(1, 6)
    def visit_code_inline(self, token):
        self._text(token.content)

    @use_font("literal")
    @use_color(7, -1)
    def visit_fence(self, token):
        if token.info and directive_pattern.match(token.info):
            return self._directive(token)

        content = token.content

        # Draw background
        hls = [self.font.text_width(line) for line in content.splitlines()]
        lh = self.font.text_width("あ")  # Use the width of "あ" as the font height
        w = lh + max(hls)
        h = lh + len(hls) * lh  # Extra row for padding
        self.img.rect(self.x, self.y, w, h, 0)

        # Draw content
        self._indent(WINDOW_PADDING)
        self.y += lh // 2

        if token.info:
            self._highlight(token)
        else:
            for line in content.splitlines():
                self._text(line)
                self._crlf()

        self.y += DEFAULT_LINE_HEIGHT // 2
        self._dedent()

    def _directive(self, token):
        """Process a directive block.

        ```{directive} args
        :opt1: value1

        content
        ```

        - `{figure}`: Display an image or app
          - args = "filename.*"
            - `.py`: load as a Pyxel app
            - `.png`, `.jpg`: load as an image
            - `.*`: try the above in order
          - options:
            - `scale`: 50 (percentage notation like "50%" is not supported)
            - `width`: 200 (pixel notation like "200px" is not supported)
            - `height`: 100 (pixel notation like "100px" is not supported)
        """
        m = directive_pattern.match(token.info)
        directive, args = m.groups()
        if directive != "figure":
            print("unsupported directive", directive)
            return
        options = dict(directive_option_pattern.findall(token.content))
        slide = self.app.slides[self.page]
        path = slide.path / args
        matches = {}  # .ext : path

        if path.suffix == ".*":
            for fname in path.parent.glob(path.name):
                if fname.suffix in [".py", ".png", ".jpg"]:
                    matches[fname.suffix] = fname
        else:
            matches[path.suffix] = path

        if ".py" in matches:
            s = int(options.pop("scale", 100)) / 100 if "scale" in options else None
            w = int(options.pop("width", 355))
            h = int(options.pop("height", 200))
            module_file = matches[".py"].relative_to(Path().absolute())
            self.app.child_apps[self.page] = ChildAppProxy(str(module_file), self.x, self.y, w, h, s)
            if options:
                print("Unsupported options", options)
            return

        for ext in (".png", ".jpg"):
            if ext not in matches:
                continue
            p = pyxel.Image.from_image(str(matches[ext]))
            if "scale" in options:
                s = int(options["scale"]) / 100
            else:
                s = self.img.width / max(p.width, self.img.width)
            x, y, w, h = self.x, self.y, p.width, p.height
            lm = max(int(self.img.width - w * s) // 2, 0)
            self.img.blt(
                lm + x - int(w * (1 - s) / 2),
                y - int(h * (1 - s) / 2),
                p,
                0,
                0,
                w,
                h,
                scale=s,
            )
            return

        print("Not Found.", args)

    def _highlight(self, token):
        import pygments
        from pygments.formatters import RawTokenFormatter
        from pygments.lexers import get_lexer_by_name

        lexer = get_lexer_by_name(token.info, stripall=True)
        formatter = RawTokenFormatter()
        hl = pygments.highlight(token.content, lexer, formatter).decode("utf-8")

        for line in hl.splitlines():
            token, value = line.split("\t")
            value = value.strip("'")
            match token:
                case "Token.Text.Whitespace" if value == "\\n":
                    self._crlf()
                case s if s.startswith("Token.Keyword"):
                    with with_color(self, 6, -1):
                        self._text(value)
                case "Token.Operator.Word":
                    with with_color(self, 2, -1):
                        self._text(value)
                case "Token.Literal.String.Double":
                    with with_color(self, 10, -1):
                        self._text(value)
                case _:
                    self._text(value)

    def visit_hardbreak(self, token):
        self._crlf()

    def visit_softbreak(self, token):
        self._crlf()

    def visit_html_inline(self, token):
        if token.content.strip() == '<br>':
            self._crlf(wrap_margin=True)

    def visit_html_block(self, token):
        if token.content.strip() == '<br>':
            self._crlf(margin=True)


# micropip requires async/await
async def main():
    if sys.platform == "emscripten":
        import micropip
        print("Installing ...")
        await micropip.install([
            "markdown-it-py[linkify]",
            "pygments"
        ])
        print("installed successfully")

    App()


if __name__ == "__main__":
    if sys.platform == "emscripten":
        # On Pyodide, use the existing event loop
        asyncio.ensure_future(main())
    else:
        # Locally, run with a new event loop
        asyncio.run(main())
