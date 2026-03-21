# Creating Presentation Slides <br> with <br> the Retro Game Engine Pyxel

PythonASIA 2026 \
2026.03.21 \
@shimizukawa

## Introduction

### Introduction

Agenda

- This slide
- The Retro Game Engine Pyxel
- The Retro Presentation Slide
- Markdown tools for Presentation

### What is this slide?

"[Pyxel]" is a tool that lets you make Retro-Games with Python.
I built this "Retro Presentation Slide" using Pyxel.
I'm going to talk about how I did it.

[Pyxel]: https://github.com/kitao/pyxel

```{figure} assets/face-dot.png
:scale: 70
```

<br>

Who am I?

- Takayuki Shimizukawa
- I used to maintain Sphinx - documentation generator.
- I started programming Around 1990, to create games.
- But, C, ASM, and DirectX were too hard to learn.
- Now, Pyxel helps me create 1990-like games again and build the   games I always dreamed of!

### What is the Retro Game Engine Pyxel?

Pyxel is a retro game engine for Python.
Developed by Kitao-san.

Pyxel is attractive:

- Ability to create NES-like retro games in Python
- Simple and intuitive API
- Expressive power limited to 16-colors and 4-sounds

According to Kitao-san,
-- "No docs for the advanced API, you’ll improve your programming skills as you discover and master it."

I like this philosophy!

### What are Retro Presentation Slides?

On top of Pyxel limitation, I created a presentation-slide viewer that requires expressive power.

- Why I made it
  - At [an event], I gave a talk called "Games I wanted to make in 1990, now built with Pyxel."
  - While making those slides, I thought: "What if the slides themselves were also built with Pyxel?" — and so I did it!

I will explain how I built it.

[an event]: https://www.freia.jp/taka/blog/2025/02/pyconshizuoka2024/index.html


## Pyxel Features Used in<br>Retro Presentation Slides

### Pyxel Features Used in Retro Presentation Slides

Here are the Pyxel-related features I used.<br>

- Displaying Japanese text
- Image banks
- Embedding images
- Page-turn animation using dithering
- Embedding a Pyxel app inside a slide

### Displaying Japanese Text

I used Japanese 日本語 BDF fonts (Bitmap Distribution Format).

- BDF is a text-based format that stores bitmap images for each character code.
- I used fonts from http://openlab.ring.gr.jp/efont/unicode/
  - They support Japanese with Unicode and come in large sizes.
- I did NOT use tools that convert TrueType fonts to BDF.
  - I wanted to avoid licensing and distribution issues.

```python
font_title     = pyxel.Font("assets/b24.bdf")
font_pagetitle = pyxel.Font("assets/b16_b.bdf")
font_default   = pyxel.Font("assets/b12.bdf")
font_bold      = pyxel.Font("assets/b12_b.bdf")
font_italic    = pyxel.Font("assets/b12_i.bdf")
```

### Image Banks

I use multiple custom image banks to avoid conflicts.

- Two Pyxel image banks are used for the slide-transition animation.
- Another bank holds the character images that match the slide progress.
- Yet another bank is used to draw the child app and overlay it on the slide.

```python
renderd_page_bank = [
    pyxel.Image(WIDTH, HEIGHT),
    pyxel.Image(WIDTH, HEIGHT),
]
player_image = pyxel.Image.from_image("assets/urban_rpg.png")
```

### Page-Turn Animation with Dithering

I use Pyxel's `dither` function to blend two slides together during a page transition.
            
```python
new_img = self.get_rendered_img(self.page)
old_img = self.get_rendered_img(old_page)
# old
pyxel.dither(rate)
pyxel.blt(old_x, old_y, old_img, 0, 0, WIDTH, HEIGHT, 7)
# new
pyxel.dither(1 - rate)
pyxel.blt(new_x, new_y, new_img, 0, 0, WIDTH, HEIGHT, 7)
pyxel.dither(1)
```

### Embedding a Pyxel App in a Slide 1/2

The mouse focuses on the child app, and control is passed to it.

```{figure} assets/typinggame.*
:scale: 100
:width: 300
:height: 165
```

### Embedding a Pyxel App in a Slide 2/2

The child app draws into an image bank, which is then overlaid on the slide.

```{figure} assets/jumpman.*
:scale: 170
:width: 220
:height: 160
```

## Slide Features of<br>Retro Presentation Slides

### Slide Features of Retro Presentation Slides

Here are the slide-related features I used. <br>

- Reference: Markdown Slide Renderers
- Tech stack
- Architecture
- Layout, style, and behavior
- Code fences (+ syntax highlighting)
- Displaying images

### Reference: Markdown Slide Renderers

Using Markdown to write slides is very convenient.
You don't have to worry about layout, and it's easy to share and reuse.

There are several tools that convert Markdown into HTML slides.
They all use HTML as the renderer.

- [Slidev] : A slide tool based on Vue.js
- [Remark.js] : Renders Markdown slides in the browser
- [Reveal.js] : An HTML slide framework
  - [sphinx-revealjs] is a [Sphinx] extension that uses it

I used these tools as a reference and built my own version with Pyxel.

[Reveal.js]: https://revealjs.com/
[Remark.js]: https://remarkjs.com/
[Slidev]: https://sli.dev/
[Sphinx]: https://www.sphinx-doc.org/en/master/
[sphinx-revealjs]: https://sphinx-revealjs.readthedocs.io/

### Tech Stack

Libraries used

- `markdown-it-py`: Markdown parser
- `pygments`: Code syntax highlighting

<br>

I also referred to these for implementation, syntax, and behavior:

- `myst-parser`: Extended Markdown syntax
- `sphinx-revealjs`: Sphinx extension for Reveal.js

### Architecture

1. Loading
   - `markdownit-py` splits the Markdown into tokens.
   - Tokens are stored in a tree structure, organized by slide.
2. Rendering
   - The current page is rendered using the Visitor pattern.
   - Text is laid out based on the Markdown syntax.
   - Two image banks handle the slide-flip animation.
3. Controls
   - Keyboard, mouse, and gamepad to move between pages.
   - Ctrl+R to reload the Markdown file.


### Layout, Style, and Behavior

Supported Markdown syntax:

- Heading 1, 2, 3 = slide title, section title, page title
- Unordered and ordered lists
- **bold**, *italic*,  `literal`
- URL link: https://example.com
- Code fences (+ syntax highlighting)
- Image display ( `{figure} file.png` )
- Pyxel App display ( `{figure} file.py` )

(HTML layout engines are really well-made, aren't they...)

### Code Fences (+ Syntax Highlighting)

- `pygments`' `RawTokenFormatter` is used to tokenize code.
- Tokens in a list are rendered one by one using `for` and `match case`.
  ```python
  hl = pygments.highlight(content, lexer, formatter)
  for line in hl.decode("utf-8").splitlines():
      token, value = line.split("\t")
      match token:
          case "Token.Operator.Word":
              with with_color(self, 2, -1):
                  self._text(value)
          ...
          case _:
              self._text(value)
  ```


### Displaying Images

- Images are loaded using `pyxel.Image.from_image`.
- However, since the screen resolution is low, large images can look blurry.

```python
p = pyxel.Image.from_image(filename)
x, y, w, h = self.x, self.y, p.width, p.height
s = 0.5
self.img.blt(
    x - int(w * (1 - s) / 2),
    y - int(h * (1 - s) / 2),
    p,
    0, 0, w, h,
    scale=s,
)
```

## Conclusion

### Conclusion

For some reason, I never seem to make progress on actual game development!<br>

- I built retro-style presentation slides using Pyxel.
- You can create slides using Markdown syntax.
- You can embed Pyxel games and run them during your presentation.
- The source code is available here:
  - https://github.com/shimizukawa/pyxel-slide-pyasia-2026

