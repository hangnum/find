"""CLI application for NL-Find."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from nl_find.config.settings import get_settings
from nl_find.core.exceptions import (
    InvalidPathError,
    LLMConnectionError,
    LLMParseError,
    MissingAPIKeyError,
)
from nl_find.core.executor import SearchExecutor
from nl_find.core.llm_parser import LLMParser
from nl_find.core.models import SearchParams, SearchQuery, SortField, SortOrder

app = typer.Typer(
    name="nfi",
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
    path: Path | None = typer.Option(
        None, "--path", "-p", help="Directory to search in"
    ),
    limit: int | None = typer.Option(
        None, "--limit", "-n", help="Maximum number of results (default: from settings)"
    ),
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
        nfi search "找出最近修改的Python文件"
        nfi search "大于10MB的视频文件" --path ./videos
        nfi search "*.py" --no-llm --path ./src
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
    try:
        sort_field = SortField(sort)
    except ValueError:
        console.print(f"[yellow]Unknown sort field '{sort}', using 'name'[/yellow]")
        sort_field = SortField.NAME
    sort_order = SortOrder.DESC if desc else SortOrder.ASC

    # Use limit from settings if not explicitly provided
    actual_limit = limit if limit is not None else settings.search.max_results

    params = SearchParams(
        query=search_query,
        sort_by=sort_field,
        sort_order=sort_order,
        limit=actual_limit,
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
    from nl_find import __version__

    console.print(f"nfi version {__version__}")


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
