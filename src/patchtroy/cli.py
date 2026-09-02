"""Command-line interface for Patchtroy."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from patchtroy.crawler import Patchtroy
from patchtroy.models import PatchtroyConfig

__version__ = "0.4.4"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="patchtroy",
        description="Undetected stealth web scraper & markdown extractor for LLMs.",
    )
    parser.add_argument("urls", nargs="*", help="Target URL(s) to scrape or 'serve' command")
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start the FastAPI REST microservice",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host address for REST microservice (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=4013,
        help="Port for REST microservice (default: 4013)",
    )
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
        "--screenshot",
        help="Capture and save screenshot to specified file path (e.g. page.png)",
    )
    parser.add_argument(
        "--full-page",
        action="store_true",
        help="Capture full-page screenshot instead of viewport only",
    )
    parser.add_argument(
        "--pdf",
        help="Generate and save PDF to specified file path (headless Chromium only)",
    )
    parser.add_argument(
        "--proxy",
        help="Single proxy URL (e.g. http://user:pass@host:port)",
    )
    parser.add_argument(
        "--proxy-file",
        help="Path to proxy file for automatic proxy rotation",
    )
    parser.add_argument(
        "--proxy-strategy",
        choices=["round-robin", "random"],
        default="round-robin",
        help="Proxy rotation strategy (default: round-robin)",
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=5,
        help="Maximum concurrent browser contexts for batch scraping (default: 5)",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"patchtroy {__version__}"
    )

    args = parser.parse_args(argv)

    # Launch REST microservice if requested
    if args.serve or (args.urls and args.urls[0] == "serve"):
        from patchtroy.server import run_server
        sys.stderr.write(f"[Patchtroy] Starting REST API on {args.host}:{args.port}...\n")
        run_server(host=args.host, port=args.port)
        return 0

    if not args.urls:
        parser.print_help()
        return 1

    # Configure proxy settings
    proxies = args.proxy_file if args.proxy_file else None

    config = PatchtroyConfig(
        headless=not args.headful,
        browser_timeout_s=args.timeout,
        wait_for=args.wait_for,
        proxy=args.proxy,
        proxies=proxies,
        proxy_strategy=args.proxy_strategy,
        max_concurrency=args.concurrency,
        screenshot=bool(args.screenshot),
        full_page_screenshot=args.full_page,
        screenshot_path=args.screenshot,
        pdf=bool(args.pdf),
        pdf_path=args.pdf,
    )

    crawler = Patchtroy(config)

    # Single URL execution
    if len(args.urls) == 1:
        target_url = args.urls[0]
        result = crawler.scrape(target_url)

        if not result.success and not result.markdown:
            sys.stderr.write(f"Error scraping {target_url}: {result.error}\n")
            return 1

        if args.format == "json":
            # Avoid serializing raw media bytes directly into standard JSON
            dump_data = result.model_dump(exclude={"screenshot_bytes", "pdf_bytes"})
            content = json.dumps(dump_data, indent=2, ensure_ascii=False)
        elif args.format == "html":
            content = result.html
        else:
            header = f"# {result.title}\n\nSource: {result.url}\n\n" if result.title else ""
            content = header + result.markdown

        if args.output:
            Path(args.output).write_text(content, encoding="utf-8")
            sys.stderr.write(f"[Patchtroy] Extracted content saved to {args.output} ({len(content)} chars)\n")
        else:
            print(content)

        if args.screenshot and result.screenshot_bytes:
            sys.stderr.write(f"[Patchtroy] Screenshot saved to {args.screenshot}\n")
        if args.pdf and result.pdf_bytes:
            sys.stderr.write(f"[Patchtroy] PDF saved to {args.pdf}\n")

        return 0

    # Batch URLs execution
    sys.stderr.write(f"[Patchtroy] Batch scraping {len(args.urls)} URLs (concurrency: {args.concurrency})...\n")
    results = crawler.scrape_many(args.urls)

    if args.format == "json":
        dump_data = [
            r.model_dump(exclude={"screenshot_bytes", "pdf_bytes"})
            for r in results
        ]
        content = json.dumps(dump_data, indent=2, ensure_ascii=False)
    else:
        combined = []
        for r in results:
            if r.success:
                header = f"# {r.title}\n\nSource: {r.url}\n\n" if r.title else f"Source: {r.url}\n\n"
                combined.append(header + r.markdown)
            else:
                combined.append(f"<!-- Failed: {r.url} ({r.error}) -->")
        content = "\n\n---\n\n".join(combined)

    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
        sys.stderr.write(f"[Patchtroy] Batch results saved to {args.output}\n")
    else:
        print(content)

    return 0


if __name__ == "__main__":
    sys.exit(main())
