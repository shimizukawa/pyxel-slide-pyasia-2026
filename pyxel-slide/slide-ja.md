# Pyxelで作る<br>レトロプレゼンスライド

Pyxel Advent Calendar 2025 \
2025.12.16 \
@shimizukawa

## はじめに

### はじめに

- この記事/スライドは？
- レトロプレゼンスライド、って何？
- Markdownスライドレンダラーとは

### この記事/スライドは？

この記事はPythonでレトロゲームが作れる「[Pyxel]」のアドベントカレンダー、「[Pyxel Advent Calendar 2025]」の16日目の記事です。
よろしくお願いします。

<br>

[Pyxel]: https://github.com/kitao/pyxel
[Pyxel Advent Calendar 2025]: https://qiita.com/advent-calendar/2025/pyxel


書いた人: @shimizukawa です。

```{figure} assets/face-dot.png
:scale: 50
```

<br>

<br>

- 1990年頃にゲームを作りたくてプログラミングを始めました
- 当時はC言語、ASM、DirectXとハードルが高くて未完ばかりでした
- Pyxelで、あの頃作りたかったゲーム作りに再挑戦中です


### レトロプレゼンスライド、って何？


- レトロプレゼンスライド
  - レトロゲームエンジンで動作する、プレゼンテーションスライド表示アプリケーションです。
- 作ったきっかけ
  - [あるイベント]で「1990年頃に作りたかったゲームをPyxelで作った」というプレゼンをしました。
  - スライドを作りながら、それならプレゼンスライド自体もPyxelで作ったら面白いのでは、と思って作りました。

この記事では、その実装方法を紹介します。

[あるイベント]: https://www.freia.jp/taka/blog/2025/02/pyconshizuoka2024/index.html


## レトロプレゼンスライドの<br>Pyxel要素

### レトロプレゼンスライドのPyxel要素

Pixel関連の技術要素を紹介します。<br>

- 日本語文字表示
- 画像バンク
- 画像埋め込み表示
- ディザリングによるページ切替アニメーション
- Pyxelアプリをスライド内に埋め込み

### 日本語文字表示

日本語BDFフォント（Bitmap Distribution Format）を使いました。

- テキストで定義された、文字コードに対応したビットマップ情報
- 採用 http://openlab.ring.gr.jp/efont/unicode/
  - 日本語をUnicodeで扱えて、大きい文字サイズが用意されている
- 不採用: TrueTypeフォントからBDFに変換するツール
  - 配布とライセンスの問題を避けたかったため

```python
font_title     = pyxel.Font("assets/b24.bdf")
font_pagetitle = pyxel.Font("assets/b16_b.bdf")
font_default   = pyxel.Font("assets/b12.bdf")
font_bold      = pyxel.Font("assets/b12_b.bdf")
font_italic    = pyxel.Font("assets/b12_i.bdf")
```

### 画像バンク

独自の画像バンクを複数使って競合を避けています。

- Pyxelの画像バンクを2つ使って、スライド切替アニメーション
- スライド進捗に合わせたキャラクター描画用画像バンク
- さらに、別の画像バンクに子アプリを描画してオーバーレイ

```python
renderd_page_bank = [
    pyxel.Image(WIDTH, HEIGHT),
    pyxel.Image(WIDTH, HEIGHT),
]
player_image = pyxel.Image.from_image("assets/urban_rpg.png")
```

### ditherによるページ切替アニメーション

Pyxelの `dither` 関数を使って、2つのスライドを合成しながら入れ替え
            
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

### Pyxelアプリをスライド内に埋め込み 1/2

マウスを子アプリにフォーカスして、子アプリに制御を渡します。

```{figure} assets/typinggame.*
:scale: 100
:width: 300
:height: 165
```

### Pyxelアプリをスライド内に埋め込み 2/2

子アプリは画像バンクに書き込み、スライドにオーバーレイしてます。

```{figure} assets/jumpman.*
:scale: 170
:width: 220
:height: 160
```

## レトロプレゼンスライドの<br>スライド要素

### レトロプレゼンスライドのスライド要素

スライド関連の技術要素を紹介します。 <br>

- 参考: Markdownスライドレンダラー
- 技術スタック
- アーキテクチャ
- レイアウト、表現、動作
- コードフェンス（+ハイライト）
- 画像表示

### 参考: Markdownスライドレンダラー

スライド作りにMarkdown記法を使うと便利です。
レイアウトに悩まされず、公開や再利用も楽になります。

MarkdownをHTMLスライドに変換するツールはいくつかあります。
これらはレンダラーにHTMLを使っています。

- [Slidev] : Vue.jsベースのスライド作成ツール
- [Remark.js] : ブラウザ上でMarkdownスライドをレンダリング
- [Reveal.js] : HTMLスライドフレームワーク
  - [Sphinx] に組み込む [sphinx-revealjs] 拡張

今回は、こういったツールを参考に、Pyxelで実装しました。

[Reveal.js]: https://revealjs.com/
[Remark.js]: https://remarkjs.com/
[Slidev]: https://sli.dev/
[Sphinx]: https://www.sphinx-doc.org/ja/master/
[sphinx-revealjs]: https://sphinx-revealjs.readthedocs.io/

### 技術スタック

利用ライブラリ

- `markdown-it-py`: Markdownパーサー
- `pygments`: コードハイライト

<br>

実装、記法、動作仕様は、以下を参考にしました。

- `myst-parser`: Markdown記法の拡張
- `sphinx-revealjs`: SphinxのReveal.js拡張

### アーキテクチャ

1. 読み込み
   - `markdownit-py` でMarkdownをトークンに分割
   - 木構造のトークンをスライド単位で保持
2. 描画
   - 見ているページをVisitorパターンでレンダリング
   - 記法に合わせて文字をレイアウト
   - 2枚のバンクでスライドめくりアニメーション
3. 操作
   - キーボード、マウス、パッドでページ移動
   - Ctrl+R でMarkdownを再読み込み


### レイアウト、表現、動作

対応している記法

- ヘディング1,2,3 = スライド,セクション,ページタイトル
- 番号なし,番号つき箇条書き
- **強調**, *斜体*,  `literal`
- URL link: https://example.com
- コードフェンス（+ハイライト）
- 画像読み込み ( `{figure} file.png` )
- Pyxel App 読み込み ( `{figure} file.py` )

（HTMLのレイアウトエンジンは良く出来てるなあ...）

### コードフェンス（+ハイライト）

- `pygments` の `RawTokenFormatter` でtokenize
- リスト構造のTokenを for match case で順次レンダリング
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


### 画像埋め込み表示

- `pyxel.Image.from_image` で画像を読み込み
- ただし画面解像度が低いので、大きな画像は潰れてしまう

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

## おわりに

### おわりに

なぜか、今日もゲーム作りが進みません！<br>

- Pyxelでレトロ調プレゼンスライドを作りました
- Markdown記法でスライドを作成できます
- Pyxelで作ったゲームを埋め込んでプレゼンできます
- ソースコードは以下のリポジトリにあります
  - https://github.com/shimizukawa/pyxel-slide-2025

