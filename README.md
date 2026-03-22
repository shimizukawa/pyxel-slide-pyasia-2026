# PythonASIA 2026 / 2026.03.21 @ Manila, Philippines

- Event: https://2026.pythonasia.org/
- Talk: https://pretalx.com/python-asia-2026/talk/SHDM83/
- Slide: https://shimizukawa.github.io/pyxel-slide-pyasia-2026/

## Links for PythonASIA 2026

1. Pyxel Repo https://github.com/kitao/pyxel
2. Pyxel User Guide https://kitao.github.io/pyxel/web/user-guide/
3. Pyxel Showcase https://kitao.github.io/pyxel/web/showcase/
4. My Pyxel Apps https://shimizukawa.github.io/pyxel-app/
5. My Presentation Repo https://github.com/shimizukawa/pyxel-slide-pyasia-2026/
6. My Presentation Slide https://shimizukawa.github.io/pyxel-slide-pyasia-2026/
7. My Presentation Slide2 https://shimizukawa.github.io/pyxel-slide-pyasia-2026/revealjs/slide-en.html

## Descriptions

"Pyxel Slide" renders markdown slides on Pyxel retro game engine for Python.

Introducing Slides at PythonASIA 2026:

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
- Function
  - 0: Debug mode
  - 1: Paging mode
  - 2: Switch slide / chile app
  - Ctrl+R: Reload
  - Ctrl+Q: Quit

Gamepad

- Move:
  - BUTTON1: Next slide
  - BUTTON2: Previous slide
  - DOWN: Next slide in section
  - UP: Previous slide in section
  - RIGHT: Next section
  - LEFT: Previous section
- Function
  - X: Switch slide / chile app
  - START: Reload
  - BACK: Paging mode
  - GUIDE: Debug mode

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
