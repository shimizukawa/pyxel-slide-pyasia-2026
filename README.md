# Python ASIA 2026 / 2026.03.21 @ Manila, Philippines

Pyxel Slide renders markdown slides on Pyxel retro game engine for Python.

Pyxel Slide Demo

- https://shimizukawa.github.io/pyxel-slide-pyasia-2026/

Sphinx-Reveal.js Version

- https://shimizukawa.github.io/pyxel-slide-pyasia-2026/revealjs/slide-en.html

## Run

Invoke Pyxel Slide App

```shell
uv run make.py run
```

Build Pyxel Slide App package

```shell
uv run make.py package
```

Build Sphinx-Reveal.js version

```shell
uv run make.py revealjs
```

## Available Controls

Keyboard

- Move:
  - Space: Next slide
  - Shift+Space: Previous slide
  - Down: Next slide in section
  - Up: Previous slide in section
  - Right: Next section
  - Left: Previous section
- Reload: Ctrl+R
- Quit: Ctrl+Q

Gamepad

- Move:
  - BUTTON1: Next slide
  - BUTTON2: Previous slide
  - DOWN: Next slide in section
  - UP: Previous slide in section
  - RIGHT: Next section
  - LEFT: Previous section
- Reload: SELECT

## Supported Markdown Syntax

- Supported syntax
  - Heading 1 = Slide title
  - Heading 2 = Page title
  - Unordered list
  - Ordered list
  - **Bold**
  - *Italic*
  - `Literal`
  - URL link
  - Code fence (+highlight)
  - Image inclusion ( `{figure} file.png` )
  - Pyxel App inclusion ( `{figure} file.py` )
