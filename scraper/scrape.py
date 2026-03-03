#!/usr/bin/env python3
"""
TARS Scraper — Point d'entree CLI.

Usage:
  # Executer tous les jobs du config.yaml
  python scrape.py

  # Executer un job specifique
  python scrape.py --job mon-job

  # Scrape rapide (one-shot)
  python scrape.py --url https://example.com
  python scrape.py --url https://example.com --selectors "title:h1,links:a[href]"
  python scrape.py --url https://example.com --mode stealth --selectors "title:h1"

  # Crawl (spider mode) depuis le config
  python scrape.py --spider mon-spider

  # Lister les jobs disponibles
  python scrape.py --list
"""

import sys
import json
import logging
import argparse
from pathlib import Path

import yaml

from engine import fetch_page, extract_data, run_job, save_results
from spiders.generic import run_spider

SCRIPT_DIR = Path(__file__).parent
DEFAULT_CONFIG = SCRIPT_DIR / "config.yaml"
DEFAULT_OUTPUT = SCRIPT_DIR / "output"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("scraper")


def load_config(config_path):
    """Load YAML config file."""
    path = Path(config_path)
    if not path.exists():
        log.error(f"Config file not found: {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_selectors_string(s):
    """Parse a selector string like 'title:h1,links:a[href],desc:p.intro'.

    Returns dict suitable for extract_data().
    """
    selectors = {}
    for part in s.split(","):
        part = part.strip()
        if ":" in part:
            name, sel = part.split(":", 1)
            selectors[name.strip()] = sel.strip()
        else:
            selectors[part] = part
    return selectors


def cmd_quick(args):
    """Quick one-shot scrape."""
    url = args.url
    mode = args.mode
    selectors = parse_selectors_string(args.selectors) if args.selectors else {}

    options = {}
    if mode in ("dynamic", "stealth"):
        options["headless"] = not args.visible
        options["timeout"] = args.timeout * 1000  # ms
        if mode == "stealth":
            options["solve_cloudflare"] = args.cloudflare
    else:
        options["timeout"] = args.timeout

    if args.proxy:
        options["proxy"] = args.proxy

    log.info(f"Quick scrape: {url} (mode={mode})")
    response = fetch_page(url, mode=mode, **options)

    if selectors:
        data = extract_data(response, selectors)
    else:
        # Default: extract title, all links, meta description
        data = {
            "_url": response.url,
            "_status": response.status,
            "title": response.css("title")[0].text if response.css("title") else None,
            "h1": [el.text for el in response.css("h1")] if response.css("h1") else [],
            "links": [el.attrib.get("href", "") for el in response.css("a[href]")][:50],
            "meta_description": (
                response.css('meta[name="description"]')[0].attrib.get("content", "")
                if response.css('meta[name="description"]')
                else None
            ),
        }

    if args.output:
        fmt = args.format or "json"
        save_results([data], {"format": fmt, "file": args.output}, str(DEFAULT_OUTPUT))
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))

    return data


def cmd_jobs(args):
    """Run jobs from config."""
    config = load_config(args.config)
    jobs = config.get("jobs", [])

    if args.job:
        jobs = [j for j in jobs if j["name"] == args.job]
        if not jobs:
            log.error(f"Job '{args.job}' not found in config")
            sys.exit(1)

    all_results = {}
    for job_config in jobs:
        results = run_job(job_config, output_dir=str(DEFAULT_OUTPUT))
        all_results[job_config["name"]] = results

    return all_results


def cmd_spider(args):
    """Run a spider from config."""
    config = load_config(args.config)
    spiders = config.get("spiders", [])

    spider_config = None
    for s in spiders:
        if s["name"] == args.spider:
            spider_config = s
            break

    if not spider_config:
        log.error(f"Spider '{args.spider}' not found in config")
        sys.exit(1)

    result = run_spider(spider_config, output_dir=str(DEFAULT_OUTPUT))
    log.info(f"Crawl stats: {json.dumps(result.stats.to_dict(), indent=2)}")
    return result


def cmd_list(args):
    """List available jobs and spiders from config."""
    config = load_config(args.config)

    print("\n=== JOBS ===")
    for job in config.get("jobs", []):
        urls = job.get("urls", [job.get("url", "?")])
        mode = job.get("mode", "basic")
        print(f"  {job['name']:30s}  mode={mode:8s}  urls={len(urls)}")

    print("\n=== SPIDERS ===")
    for spider in config.get("spiders", []):
        domains = spider.get("allowed_domains", [])
        concurrent = spider.get("concurrent_requests", 4)
        print(f"  {spider['name']:30s}  concurrent={concurrent}  domains={domains}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="TARS Scraper — Scrape tout, partout.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--config", "-c", default=str(DEFAULT_CONFIG), help="Config YAML file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Debug logging")

    sub = parser.add_subparsers(dest="command")

    # Quick scrape
    quick = sub.add_parser("quick", help="Scrape rapide d'une URL")
    quick.add_argument("url", help="URL a scraper")
    quick.add_argument("--mode", "-m", choices=["basic", "dynamic", "stealth"], default="basic")
    quick.add_argument("--selectors", "-s", help="Selecteurs CSS: 'nom:selecteur,nom2:selecteur2'")
    quick.add_argument("--proxy", "-p", help="Proxy URL")
    quick.add_argument("--timeout", "-t", type=int, default=30, help="Timeout en secondes")
    quick.add_argument("--visible", action="store_true", help="Mode visible (non-headless)")
    quick.add_argument("--cloudflare", action="store_true", help="Bypass Cloudflare (mode stealth)")
    quick.add_argument("--output", "-o", help="Fichier de sortie")
    quick.add_argument("--format", "-f", choices=["json", "jsonl", "csv"], default="json")

    # Run jobs
    jobs = sub.add_parser("run", help="Executer des jobs depuis le config")
    jobs.add_argument("--job", "-j", help="Nom du job (tous si omis)")

    # Run spider
    spider = sub.add_parser("crawl", help="Lancer un spider depuis le config")
    spider.add_argument("spider", help="Nom du spider")

    # List
    sub.add_parser("list", help="Lister les jobs et spiders disponibles")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.command == "quick":
        cmd_quick(args)
    elif args.command == "run":
        cmd_jobs(args)
    elif args.command == "crawl":
        cmd_spider(args)
    elif args.command == "list":
        cmd_list(args)
    else:
        # Default: run all jobs if no subcommand
        if Path(args.config).exists():
            args.job = None
            cmd_jobs(args)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
