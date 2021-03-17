import asyncio
import subprocess

import typer
import uvicorn

from blog_app import _debug_app
from blog_app.database import create_tables
from blog_app.settings import load as load_settings

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


@app.command()
def test(coverage: bool = True, coverage_report: str = "term,html"):
    args = ["pytest", "--doctest-modules"]

    if coverage:
        args.append(f"--cov=blog_app")

        if coverage_report:
            args.extend(
                f"--cov-report={report}" for report in coverage_report.split(",")
            )

    subprocess.run(args)


@app.command()
def server(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run(
        "blog_app:_debug_app",
        host=host,
        port=port,
        log_level="info",
        workers=1,
        reload=True,
    )


@app.command()
def debug(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run(_debug_app, host=host, port=port, log_level="info")


@app.command()
def create_model():
    settings = load_settings()
    asyncio.run(create_tables(settings.database))


if __name__ == "__main__":
    app()
