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

### This slide

This slide is built with "[Pyxel]".
Not just impl directly, you can show your own Markdown on it!
I'm going to talk about the essence.

[Pyxel]: https://github.com/kitao/pyxel

```{figure} assets/face-dot.png
:scale: 70
```

<br>

Who am I?

- Takayuki Shimizukawa
- Co-maintainer of Sphinx
- To create games, I started programming in 199x
- But, C, ASM, and DirectX were too hard to learn
- Now, Pyxel helps me create 1990-like games again and build the   games I always dreamed of!

### What is the Retro Game Engine Pyxel?

*PYXEL* is developed by Kitao-san.
**ATTRACTIVE**  points:

- Retro ( NES-like ) Visual
- Simple and intuitive API
- Limited expressive power (Color, sound, resolution, ...)

According to Kitao-san,
-- "No docs for the advanced API, you’ll improve your programming skills as you discover and master it."

I like this philosophy!

### What are Retro Presentation Slides?

On top of Pyxel limitation, I created a Presentation viewer that **REQUIRES** expressive power.

Why?

- At [an event], I talked about my prog roots were in game prog.
- I realized that creating presentation slides with Pyxel would be a **FUN**!
- And so I did it!

How?

In my Sphinx dev experience, I know how to parse text and render it, which libraries to use, how to combine them.
In this talk, I will give you the essence.

[an event]: https://www.freia.jp/taka/blog/2025/02/pyconshizuoka2024/index.html


## How to use Pyxel for<br>Retro Presentation Slides

### How to use Pyxel for Retro Presentation Slides

Here are the Pyxel-related features I used.<br>

- Displaying Japanese text
- Image banks
- Slide-transition animation
- Embedding images
- Embedding a Pyxel app

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

I use multiple custom Pyxel image banks for Expressive Power.

- Two image banks are used for the slide-transition animation.
- Another bank holds the character images.
- Yet another bank is used for more features.

```python
renderd_page_bank = [
    pyxel.Image(WIDTH, HEIGHT),
    pyxel.Image(WIDTH, HEIGHT),
]
player_image = pyxel.Image.from_image("assets/urban_rpg.png")
```

### Slide-Transition Animation with Dithering

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

### Embedding images

- Images are loaded using `pyxel.Image.from_image`.

```python
p = pyxel.Image.from_image(filename)
s = 0.5
img.blt(
    x - int(w * (1 - s) / 2),
    y - int(h * (1 - s) / 2),
    p, 0, 0, w, h, scale=s,
)
```

```{figure} assets/pyasia2026.png
:scale: 70
```

Due to limitation
colors and resolution,
images can look blurry.

### Embedding a Pyxel App 1/2

The mouse focuses on the child app, and control is passed to it.

```{figure} assets/typinggame.*
:scale: 100
:width: 300
:height: 165
```

### Embedding a Pyxel App 2/2

The child app draws into an image bank, then blt on the slide.

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


## Conclusion

### Conclusion

For some reason, I never seem to make progress on actual game development!<br>

- I built retro-style presentation slides using Pyxel.
- You can create slides using Markdown syntax.
- You can embed Pyxel games and run them during your presentation.
- The source code is available here:
  - https://github.com/shimizukawa/pyxel-slide-pyasia-2026

