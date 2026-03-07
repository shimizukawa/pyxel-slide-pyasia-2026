# Pyxel Advent Calendar 2025 / Day 16, 2025.12.16

Markdownで書いたスライドをPyxelゲームエンジンで表示します。

Pyxelスライドのデモ

- https://shimizukawa.github.io/pyxel-slide-2025/

Sphinx-Reveal.js版

- https://shimizukawa.github.io/pyxel-slide-2025/revealjs/slide-ja.html

Blog版

- https://www.freia.jp/taka/blog/2025/12/pyxel-slide/index.html

## 実行

Pyxelアプリ起動

```shell
uv run make.py run
```

Pyxelパッケージ作成

```shell
uv run make.py package
```

Sphinx-Reveal.jsでスライド生成

```shell
uv run make.py revealjs
```

## 操作

- 移動:
  - スペース: 次のスライド
  - シフト+スペース: 前のスライド
  - 下: セクション内の次スライド
  - 上: セクション内の前スライド
  - 右: 次のセクション
  - 左: 前のセクション
- リロード: Ctrl+R
- 終了: Ctrl+Q

## サポートしている機能

- 日本語表示対応
- 対応している記法
  - ヘディング1 = スライドタイトル
  - ヘディング2 = 各ページタイトル
  - 番号なし箇条書き
  - 番号付き箇条書き
  - **強調**
  - *斜体*
  - `literal`
  - URL link
  - コードフェンス（+ハイライト）
  - 画像読み込み ( `{figure} file.png` )
  - Pyxel App 読み込み ( `{figure} file.py` )
