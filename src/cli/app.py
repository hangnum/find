"""CLI application for NL-Find."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from src.config.settings import get_settings
from src.core.exceptions import (
    InvalidPathError,
    LLMConnectionError,
    LLMParseError,
    MissingAPIKeyError,
)
from src.core.executor import SearchExecutor
from src.core.llm_parser import LLMParser
from src.core.models import SearchParams, SearchQuery, SortField, SortOrder

app = typer.Typer(
    name="nl-find",
    help="Natural language file search powered by LLM.",
    add_completion=True,
)
console = Console()


def format_size(size: int) -> str:
    """Format file size in human readable format.

    Args:
        size: Size in bytes.

    Returns:
        Formatted size string.
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def display_results(files: list, search_time: float) -> None:
    """Display search results in a table.

    Args:
        files: List of FileInfo objects.
        search_time: Time taken for search in seconds.
    """
    if not files:
        console.print("[yellow]No files found.[/yellow]")
        return

    table = Table(title=f"Found {len(files)} files in {search_time:.2f}s")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Size", justify="right", style="green")
    table.add_column("Modified", style="magenta")
    table.add_column("Path", style="dim")

    for f in files:
        table.add_row(
            f.name,
            format_size(f.size),
            f.modified.strftime("%Y-%m-%d %H:%M"),
            str(f.path.parent),
        )

    console.print(table)


@app.command()
def search(
    query: str = typer.Argument(..., help="Natural language search query"),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Directory to search in"
    ),
    limit: int = typer.Option(100, "--limit", "-n", help="Maximum number of results"),
    sort: str = typer.Option(
        "name", "--sort", "-s", help="Sort by: name, size, modified, created"
    ),
    desc: bool = typer.Option(False, "--desc", "-d", help="Sort in descending order"),
    no_llm: bool = typer.Option(
        False, "--no-llm", help="Skip LLM parsing (use direct pattern)"
    ),
) -> None:
    """Search files using natural language query.

    Examples:
        nl-find "找出最近修改的Python文件"
        nl-find "大于10MB的视频文件" --path ./videos
        nl-find "*.py" --no-llm --path ./src
    """
    settings = get_settings()
    search_path = path or settings.search.default_path

    # Parse query using LLM or directly
    if no_llm:
        # Direct pattern search without LLM
        search_query = SearchQuery(
            path=search_path,
            pattern=query,
            recursive=True,
        )
        console.print(f"[dim]Direct pattern search: {query}[/dim]")
    else:
        # Use LLM to parse natural language
        try:
            parser = LLMParser()
            with console.status("[bold green]Parsing query with LLM..."):
                search_query = parser.parse(query)
            search_query.path = search_path
            console.print(f"[dim]Parsed: extensions={search_query.extensions}, "
                          f"min_size={search_query.min_size}, "
                          f"pattern={search_query.pattern}[/dim]")
        except MissingAPIKeyError:
            console.print(
                "[red]Error: OpenAI API key not configured.[/red]\n"
                "Set OPENAI_API_KEY environment variable or use --no-llm flag."
            )
            raise typer.Exit(1)
        except LLMConnectionError as e:
            console.print(f"[red]LLM connection failed: {e}[/red]")
            raise typer.Exit(1)
        except LLMParseError as e:
            console.print(f"[red]Failed to parse query: {e}[/red]")
            raise typer.Exit(1)

    # Execute search
    sort_field = SortField(sort) if sort in SortField.__members__.values() else SortField.NAME
    sort_order = SortOrder.DESC if desc else SortOrder.ASC

    params = SearchParams(
        query=search_query,
        sort_by=sort_field,
        sort_order=sort_order,
        limit=limit,
    )

    try:
        executor = SearchExecutor()
        with console.status("[bold green]Searching..."):
            result = executor.execute(params)
        display_results(result.files, result.search_time)
    except InvalidPathError as e:
        console.print(f"[red]Invalid path: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    from src import __version__

    console.print(f"nl-find version {__version__}")


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
