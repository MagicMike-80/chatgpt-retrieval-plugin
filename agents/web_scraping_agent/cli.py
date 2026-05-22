#!/usr/bin/env python3
"""
Web Scraping Agent CLI

Usage:
    python -m agents.web_scraping_agent.cli <url> [options]

Examples:
    python -m agents.web_scraping_agent.cli https://emergent.sh
    python -m agents.web_scraping_agent.cli emergent.sh --output ./my_clone --max-pages 5
    python -m agents.web_scraping_agent.cli stripe.com --depth 1 --verbose
"""

import argparse
import logging
import sys

from .agent import WebScrapingAgent


def main():
    parser = argparse.ArgumentParser(
        description="Scrape and clone any website using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("url", help="Target URL to scrape and clone (e.g. emergent.sh)")
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output directory for the clone (default: ./clones/<domain>)",
    )
    parser.add_argument(
        "--max-pages", "-p",
        type=int,
        default=10,
        help="Maximum number of pages to scrape (default: 10)",
    )
    parser.add_argument(
        "--depth", "-d",
        type=int,
        default=2,
        help="Maximum crawl depth (default: 2)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay between requests in seconds (default: 0.5)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Anthropic API key (default: reads ANTHROPIC_API_KEY env var)",
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    print(f"\n Web Scraping Agent")
    print(f" Target : {args.url}")
    print(f" Pages  : up to {args.max_pages} (depth {args.depth})")
    print(f" Output : {args.output or 'auto'}")
    print()

    try:
        agent = WebScrapingAgent(
            anthropic_api_key=args.api_key,
            max_pages=args.max_pages,
            max_depth=args.depth,
            scrape_delay=args.delay,
        )
        result = agent.run(url=args.url, output_dir=args.output)

        print("\n Clone complete!")
        print(f" Output : {result.output_dir}")
        print(f" Index  : {result.index_path}")
        print(f" Files  : {len(result.files)}")
        print(f"\n{result.summary}")
        print(f"\n Open {result.index_path} in your browser to view the clone.")

    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Failed: {e}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == "__main__":
    main()
