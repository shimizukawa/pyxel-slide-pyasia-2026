# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "sphinx-revealjs==3.2.*",
#     "sphinx==8.*",
#     "myst-parser[linkify]==4.*",
#     "click",
# ]
# ///
import subprocess
import shutil
from pathlib import Path

import click

PACKAGE_NAME = "pyxel-slide"


@click.command()
def run():
    """Invoke Pyxel Slide App"""
    # invoke main.py in PACKAGE_NAME directory with uv
    subprocess.run(["uv", "run", "main.py"], cwd=PACKAGE_NAME)


@click.command()
def package():
    """Build Pyxel Slide App package"""
    shutil.rmtree(f"./{PACKAGE_NAME}/__pycache__", ignore_errors=True)
    shutil.rmtree(f"./{PACKAGE_NAME}/assets/__pycache__", ignore_errors=True)
    subprocess.run(
        ["uvx", "pyxel", "package", PACKAGE_NAME, f"./{PACKAGE_NAME}/main.py"]
    )

    Path("./dist").mkdir(exist_ok=True, parents=True)
    shutil.move(f"{PACKAGE_NAME}.pyxapp", f"dist/{PACKAGE_NAME}.pyxapp")
    shutil.copyfile(f"{PACKAGE_NAME}/index.html", "dist/index.html")
    shutil.copyfile(f"{PACKAGE_NAME}/slide-ja.md", "dist/slide-ja.md")
    if Path(f"./{PACKAGE_NAME}/assets").exists():
        shutil.copytree(f"./{PACKAGE_NAME}/assets", "dist/assets", dirs_exist_ok=True)


@click.command()
def revealjs():
    """Build Sphinx-Reveal.js version"""
    # invoke: sphinx-build -M revealjs PACKAGE_NAME build
    subprocess.run(
        [
            "sphinx-build",
            "-M",
            "revealjs",
            PACKAGE_NAME,
            "build",
        ]
    )
    # Open build/revealjs/slide-ja.html in browser from Python
    # slide_path = Path("build/revealjs/slide-ja.html").resolve()
    # webbrowser.open_new_tab(slide_path.as_uri())

    Path("./dist").mkdir(exist_ok=True, parents=True)
    if Path("dist/revealjs").exists():
        shutil.rmtree("dist/revealjs")
    shutil.copytree(Path("build/revealjs"), "dist/revealjs")


@click.group()
def cli():
    """pyxel-slide utility. Operate with subcommands."""


# Subcommands
cli.add_command(run)
cli.add_command(package)
cli.add_command(revealjs)

if __name__ == "__main__":
    cli()
