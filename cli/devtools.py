import subprocess
from pathlib import Path

import typer

app = typer.Typer()


@app.command()
def lint_types():
    args = ["mypy", "--check-untyped-defs", "./"]

    typer.secho("Analysing types...", fg=typer.colors.YELLOW)
    subprocess.run(args)


@app.command()
def lint_format(fix: bool = False):
    args = ["black"]

    if not fix:
        args.append("--check")

    args.append("./")

    typer.secho(
        f"{'Fixing' if fix else 'Checking'} code format...", fg=typer.colors.YELLOW
    )
    subprocess.run(args)


@app.command()
def lint(fix_format: bool = False):
    lint_types()
    lint_format(fix_format)


if __name__ == "__main__":
    app()
