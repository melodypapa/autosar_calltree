"""
Command-line interface for autosar-calltree.

This module provides the main CLI entry point using Click.
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..analyzers.call_tree_builder import CallTreeBuilder
from ..config.module_config import ModuleConfig
from ..database.function_database import FunctionDatabase
from ..generators.mermaid_generator import MermaidGenerator
from ..generators.xmi_generator import XmiGenerator
from ..version import __version__

console = Console(record=True)


@click.command()
@click.option(
    "--start-function",
    "-s",
    required=False,  # Not required if --list-functions or --search is used
    help="Name of the function to start call tree from",
)
@click.option(
    "--max-depth",
    "-d",
    default=3,
    type=int,
    help="Maximum depth to traverse (default: 3)",
)
@click.option(
    "--source-dir",
    "-i",
    default="./demo",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Source directory containing C files (default: ./demo)",
)
@click.option(
    "--output",
    "-o",
    default="call_tree.md",
    type=click.Path(),
    help="Output file path (default: call_tree.md)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["mermaid", "xmi", "both"], case_sensitive=False),
    default="mermaid",
    help="Output format (default: mermaid)",
)
@click.option(
    "--cache-dir",
    type=click.Path(file_okay=False, dir_okay=True),
    help="Cache directory (default: <source-dir>/.cache)",
)
@click.option("--no-cache", is_flag=True, help="Disable cache usage")
@click.option("--rebuild-cache", is_flag=True, help="Force rebuild of cache")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option(
    "--list-functions", "-l", is_flag=True, help="List all available functions and exit"
)
@click.option(
    "--search", type=str, help="Search for functions matching pattern and exit"
)
@click.option(
    "--no-abbreviate-rte",
    is_flag=True,
    help="Do not abbreviate RTE function names in diagrams",
)
@click.option(
    "--module-config",
    type=click.Path(exists=True),
    help="Path to YAML file mapping C files to SW modules",
)
@click.option(
    "--use-module-names",
    is_flag=True,
    help="Use SW module names as Mermaid participants (requires --module-config)",
)
@click.version_option(version=__version__, prog_name="autosar-calltree")
def cli(
    start_function: str,
    max_depth: int,
    source_dir: str,
    output: str,
    format: str,
    cache_dir: Optional[str],
    no_cache: bool,
    rebuild_cache: bool,
    verbose: bool,
    list_functions: bool,
    search: Optional[str],
    no_abbreviate_rte: bool,
    module_config: Optional[str],
    use_module_names: bool,
):
    """
    AUTOSAR Call Tree Analyzer

    Analyzes C/AUTOSAR codebases and generates function call trees
    with Mermaid sequence diagrams or XMI output.
    """
    try:
        # Print banner
        if not verbose:
            console.print(
                f"[bold cyan]AUTOSAR Call Tree Analyzer v{__version__}[/bold cyan]"
            )
            console.print()

        # Validate use_module_names requires module_config
        if use_module_names and not module_config:
            console.print(
                "[yellow]Warning:[/yellow] --use-module-names requires --module-config. "
                "Module names will not be used."
            )
            use_module_names = False

        # Load module configuration if provided
        config = None
        if module_config:
            try:
                config = ModuleConfig(Path(module_config))
                if verbose:
                    console.print(
                        f"[cyan]Loaded module configuration from {module_config}[/cyan]"
                    )
                    config_stats = config.get_statistics()
                    console.print(
                        f"  - Specific file mappings: {config_stats['specific_file_mappings']}"
                    )
                    console.print(
                        f"  - Pattern mappings: {config_stats['pattern_mappings']}"
                    )
            except Exception as e:
                console.print(f"[bold red]Error loading module config:[/bold red] {e}")
                sys.exit(1)

        # Initialize database
        use_cache = not no_cache

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=False,
        ) as progress:
            # Build database
            task = progress.add_task("", total=None)

            db = FunctionDatabase(source_dir, cache_dir=cache_dir, module_config=config)
            db.build_database(
                use_cache=use_cache, rebuild_cache=rebuild_cache, verbose=verbose
            )

            progress.update(task, completed=True)

        # Print statistics
        stats = db.get_statistics()

        if verbose:
            console.print("\n[bold]Database Statistics:[/bold]")
            table = Table(show_header=False)
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            table.add_row("Files Scanned", str(stats["total_files_scanned"]))
            table.add_row("Functions Found", str(stats["total_functions_found"]))
            table.add_row("Unique Names", str(stats["unique_function_names"]))
            table.add_row("Static Functions", str(stats["static_functions"]))
            table.add_row("Parse Errors", str(stats["parse_errors"]))
            console.print(table)

            # Print module statistics if available
            if stats.get("module_stats"):
                console.print("\n[bold]Module Distribution:[/bold]")
                for module, count in sorted(stats["module_stats"].items()):
                    console.print(f"  {module}: {count} functions")
            console.print()

        # Handle list functions
        if list_functions:
            console.print("[bold]Available Functions:[/bold]\n")
            functions = db.get_all_function_names()
            for idx, func_name in enumerate(functions, 1):
                console.print(f"{idx:4d}. {func_name}")
            console.print(f"\n[cyan]Total: {len(functions)} functions[/cyan]")
            return

        # Handle search
        if search:
            console.print()
            console.print(f"[bold]Search Results for '{search}':[/bold]\n")
            results = db.search_functions(search)
            if results:
                for func_info in results:
                    file_name = Path(func_info.file_path).name
                    console.print(
                        f"  [cyan]{func_info.name}[/cyan] "
                        f"({file_name}:{func_info.line_number})"
                    )
                console.print(f"\n[cyan]Found {len(results)} matches[/cyan]")
            else:
                console.print(
                    f"[yellow]No functions found matching '{search}'[/yellow]"
                )
            return

        # Validate start_function is provided if not using list/search
        if not start_function:
            console.print("[bold red]Error:[/bold red] --start-function is required")
            console.print("Use --list-functions to see available functions")
            sys.exit(1)

        # Build call tree
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(
                f"Building call tree for {start_function}...", total=None
            )

            builder = CallTreeBuilder(db)
            result = builder.build_tree(
                start_function=start_function,
                max_depth=max_depth,
                verbose=verbose,
            )

            progress.update(task, completed=True)

        # Check for errors
        if result.errors:
            console.print("[bold red]Errors:[/bold red]")
            for error in result.errors:
                console.print(f"  - {error}")
            sys.exit(1)

        # Print analysis statistics
        if not verbose:
            console.print("[bold]Analysis Results:[/bold]")
            console.print(
                f"  - Total functions: [cyan]{result.statistics.total_functions}[/cyan]"
            )
            console.print(
                f"  - Unique functions: [cyan]{result.statistics.unique_functions}[/cyan]"
            )
            console.print(
                f"  - Max depth: [cyan]{result.statistics.max_depth_reached}[/cyan]"
            )
            if result.statistics.circular_dependencies_found > 0:
                console.print(
                    f"  - Circular dependencies: "
                    f"[yellow]{result.statistics.circular_dependencies_found}[/yellow]"
                )
            console.print()

        # Generate output
        output_path = Path(output)

        if format in ["mermaid", "both"]:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task("Generating Mermaid diagram...", total=None)

                mermaid_output = (
                    output_path
                    if format == "mermaid"
                    else output_path.with_suffix(".mermaid.md")
                )

                generator = MermaidGenerator(
                    abbreviate_rte=not no_abbreviate_rte,
                    use_module_names=use_module_names,
                )
                generator.generate(result, str(mermaid_output))

                progress.update(task, completed=True)

            console.print(
                f"[green]Generated[/green] Mermaid diagram: [cyan]{mermaid_output}[/cyan]"
            )

        if format == "xmi":
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task("Generating XMI document...", total=None)

                xmi_output = output_path.with_suffix(".xmi") if output_path.suffix != ".xmi" else output_path

                xmi_generator = XmiGenerator(
                    use_module_names=use_module_names,
                )
                xmi_generator.generate(result, str(xmi_output))

                progress.update(task, completed=True)

            console.print(
                f"[green]Generated[/green] XMI document: [cyan]{xmi_output}[/cyan]"
            )

        if format == "both":
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task("Generating XMI document...", total=None)

                xmi_output = output_path.with_suffix(".xmi")

                xmi_generator = XmiGenerator(
                    use_module_names=use_module_names,
                )
                xmi_generator.generate(result, str(xmi_output))

                progress.update(task, completed=True)

            console.print(
                f"[green]Generated[/green] XMI document: [cyan]{xmi_output}[/cyan]"
            )

        # Print warnings for circular dependencies
        if result.circular_dependencies:
            console.print(
                "\n[bold yellow]Warning:[/bold yellow] Circular dependencies detected!"
            )
            for idx, circ_dep in enumerate(result.circular_dependencies, 1):
                cycle_str = " → ".join(circ_dep.cycle)
                console.print(
                    f"  {idx}. [yellow]{cycle_str}[/yellow] (depth {circ_dep.depth})"
                )

        console.print("\n[bold green]Analysis complete![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    cli()
