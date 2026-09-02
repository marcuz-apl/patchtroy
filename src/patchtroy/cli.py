"""Command-line interface for Patchtroy."""

from __future__ import annotations

import argparse
import json
import sys

from patchtroy.crawler import Patchtroy
from patchtroy.models import PatchtroyConfig

__version__ = "0.1.0"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="patchtroy",
        description="Undetected stealth web scraper & markdown extractor for LLMs.",
    )
    parser.add_argument("url", nargs="?", help="Target URL to scrape")
    parser.add_argument(
        "-o", "--output", help="Output file path (default: print to stdout)"
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["markdown", "json", "html"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--wait-for",
        help="CSS selector to wait for before extracting page content",
    )
    parser.add_argument(
        "--headful",
        action="store_true",
        help="Run Chromium with visible browser window (non-headless)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=25.0,
        help="Browser navigation timeout in seconds (default: 25.0)",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"patchtroy {__version__}"
    )

    args = parser.parse_args(argv)

    if not args.url:
        parser.print_help()
        return 1

    config = PatchtroyConfig(
        headless=not args.headful,
        browser_timeout_s=args.timeout,
        wait_for=args.wait_for,
    )

    crawler = Patchtroy(config)
    result = crawler.scrape(args.url)

    if not result.success and not result.markdown:
        sys.stderr.write(f"Error scraping {args.url}: {result.error}
")
        return 1

    # Format output
    if args.format == "json":
        content = json.dumps(result.model_dump(), indent=2, ensure_ascii=False)
    elif args.format == "html":
        content = result.html
    else:
        header = f"# {result.title}

Source: {result.url}

" if result.title else ""
        content = header + result.markdown

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(content)
        sys.stderr.write(f"[Patchtroy] Extracted content saved to {args.output} ({len(content)} chars)
")
    else:
        print(content)

    return 0


if __name__ == "__main__":
    sys.exit(main())
