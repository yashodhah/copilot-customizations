#!/usr/bin/env python3
"""
Unbounded grep search for large SQL repositories.
Overcomes VS Code grep_search 200-result limit and 20-second timeout.

Usage:
    python grep_search.py --pattern "customer_email" --change-id "rename-email-2026-02-01"
    python grep_search.py --pattern "FROM\s+claims" --file-glob "*.sql" --paths "patches/claims/" "patches/shared/"
"""

import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path
from typing import Optional


def parse_copilot_context(context_file: Path) -> list[str]:
    """Extract module paths from .copilot-context.md"""
    modules = []
    if not context_file.exists():
        return modules

    content = context_file.read_text()
    in_modules_section = False

    for line in content.split("\n"):
        if line.strip().startswith("modules:"):
            in_modules_section = True
            continue
        if in_modules_section:
            if line.strip().startswith("-"):
                # Extract path from "- patches/claims/"
                path = line.strip().lstrip("-").strip()
                if path:
                    modules.append(path)
            elif (
                line.strip() and not line.startswith(" ") and not line.startswith("\t")
            ):
                # End of modules section
                break

    return modules


def search_files(
    workspace_root: Path,
    pattern: str,
    paths: list[str],
    file_glob: str = "*.sql",
    case_sensitive: bool = False,
) -> list[dict]:
    """Search files for regex pattern, return all matches."""
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        print(f"Invalid regex pattern: {e}", file=sys.stderr)
        sys.exit(1)

    results = []
    files_searched = 0

    for base_path in paths:
        search_path = workspace_root / base_path
        if not search_path.exists():
            print(f"Warning: Path does not exist: {search_path}", file=sys.stderr)
            continue

        for file in search_path.rglob(file_glob):
            if not file.is_file():
                continue
            files_searched += 1

            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        if regex.search(line):
                            results.append(
                                {
                                    "file_path": str(file.relative_to(workspace_root)),
                                    "line_number": line_num,
                                    "match_content": line.strip()[:200],
                                }
                            )
            except (IOError, OSError) as e:
                print(f"Warning: Could not read {file}: {e}", file=sys.stderr)

    return results, files_searched


def write_results(
    workspace_root: Path, results: list[dict], change_id: str, metadata: dict
) -> tuple[Path, Path]:
    """Write CSV results and JSON metadata to cache directory."""
    cache_dir = workspace_root / "copilot_impact_analysis" / "search_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Write CSV
    csv_path = cache_dir / f"{change_id}_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["file_path", "line_number", "match_content"]
        )
        writer.writeheader()
        writer.writerows(results)

    # Write metadata JSON
    json_path = cache_dir / f"{change_id}_metadata.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return csv_path, json_path


def main():
    parser = argparse.ArgumentParser(
        description="Unbounded grep search for large SQL repositories"
    )
    parser.add_argument(
        "--pattern", "-p", required=True, help="Regex pattern to search for"
    )
    parser.add_argument(
        "--change-id",
        "-c",
        required=True,
        help="Identifier for this analysis (used in output filename)",
    )
    parser.add_argument(
        "--file-glob",
        "-g",
        default="*.sql",
        help="File pattern to search (default: *.sql)",
    )
    parser.add_argument(
        "--paths", nargs="*", help="Paths to search (default: from .copilot-context.md)"
    )
    parser.add_argument(
        "--workspace",
        "-w",
        type=Path,
        default=Path.cwd(),
        help="Workspace root directory (default: current directory)",
    )
    parser.add_argument(
        "--case-sensitive", action="store_true", help="Enable case-sensitive search"
    )
    parser.add_argument(
        "--json-output", action="store_true", help="Output metadata as JSON to stdout"
    )

    args = parser.parse_args()
    workspace_root = args.workspace.resolve()

    # Determine search paths
    if args.paths:
        search_paths = args.paths
    else:
        context_file = workspace_root / ".copilot-context.md"
        search_paths = parse_copilot_context(context_file)
        if not search_paths:
            print(
                "Error: No paths specified and .copilot-context.md not found or has no modules",
                file=sys.stderr,
            )
            sys.exit(1)

    # Execute search
    start_time = time.time()
    results, files_searched = search_files(
        workspace_root=workspace_root,
        pattern=args.pattern,
        paths=search_paths,
        file_glob=args.file_glob,
        case_sensitive=args.case_sensitive,
    )
    duration = time.time() - start_time

    # Build metadata
    files_matched = len(set(r["file_path"] for r in results))
    metadata = {
        "search_phase": "comprehensive",
        "pattern": args.pattern,
        "result_count": len(results),
        "files_searched": files_searched,
        "files_matched": files_matched,
        "limit_reached": False,
        "timeout": False,
        "results_file": f"copilot_impact_analysis/search_cache/{args.change_id}_results.csv",
        "metadata_file": f"copilot_impact_analysis/search_cache/{args.change_id}_metadata.json",
        "search_scope": search_paths,
        "file_glob": args.file_glob,
        "case_sensitive": args.case_sensitive,
        "duration_seconds": round(duration, 2),
    }

    # Write results
    csv_path, json_path = write_results(
        workspace_root, results, args.change_id, metadata
    )

    # Output
    if args.json_output:
        print(json.dumps(metadata, indent=2))
    else:
        print(f"Search completed in {duration:.2f}s")
        print(f"Pattern: {args.pattern}")
        print(f"Files searched: {files_searched}")
        print(f"Files matched: {files_matched}")
        print(f"Total matches: {len(results)}")
        print(f"Results: {csv_path}")
        print(f"Metadata: {json_path}")


if __name__ == "__main__":
    main()
