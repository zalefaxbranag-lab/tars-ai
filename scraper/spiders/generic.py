"""
GenericSpider — A config-driven Spider for large-scale crawling.

Uses Scrapling's Spider framework (async, concurrent, pause/resume, dedup).
Configurable via YAML: start URLs, selectors, link-following patterns, sessions.
"""

import re
import logging
from pathlib import Path

from scrapling.spiders import Spider, Request
from scrapling.fetchers import FetcherSession

log = logging.getLogger("scraper")


class GenericSpider(Spider):
    """A configurable spider that crawls sites and extracts data based on YAML config.

    Config keys:
        name: Spider name (required).
        start_urls: List of starting URLs.
        allowed_domains: Set of domains to stay within.
        selectors: Dict of field_name -> CSS selector for data extraction.
        follow_links: CSS selector for links to follow (e.g., "a[href]").
        follow_pattern: Regex pattern to filter followed URLs.
        max_pages: Maximum pages to crawl (0 = unlimited).
        concurrent_requests: Number of parallel requests.
        download_delay: Seconds between requests.
        session: Session configuration dict.
    """

    def __init__(self, config, output_dir="output"):
        self.name = config["name"]
        self.start_urls = config.get("start_urls", [])
        self.allowed_domains = set(config.get("allowed_domains", []))

        self._selectors = config.get("selectors", {})
        self._follow_links = config.get("follow_links", None)
        self._follow_pattern = re.compile(config["follow_pattern"]) if config.get("follow_pattern") else None
        self._max_pages = config.get("max_pages", 0)
        self._pages_crawled = 0
        self._output_dir = Path(output_dir)
        self._output_config = config.get("output", {"format": "jsonl"})
        self._session_config = config.get("session", {})

        self.concurrent_requests = config.get("concurrent_requests", 4)
        self.download_delay = config.get("download_delay", 0.0)

        crawldir = config.get("crawldir", None)
        super().__init__(crawldir=crawldir)

    def configure_sessions(self, manager):
        session_kwargs = {}
        sc = self._session_config

        if sc.get("proxy"):
            session_kwargs["proxy"] = sc["proxy"]
        if sc.get("timeout"):
            session_kwargs["timeout"] = sc["timeout"]
        if sc.get("headers"):
            session_kwargs["headers"] = sc["headers"]
        if sc.get("impersonate"):
            session_kwargs["impersonate"] = sc["impersonate"]
        if "stealthy_headers" in sc:
            session_kwargs["stealthy_headers"] = sc["stealthy_headers"]
        if sc.get("retries"):
            session_kwargs["retries"] = sc["retries"]

        manager.add("default", FetcherSession(**session_kwargs))

    async def parse(self, response):
        if self._max_pages and self._pages_crawled >= self._max_pages:
            return

        self._pages_crawled += 1

        # Extract data if selectors defined
        if self._selectors:
            item = {"_url": response.url, "_status": response.status}
            for field, sel_config in self._selectors.items():
                if isinstance(sel_config, str):
                    sel_config = {"selector": sel_config}

                selector = sel_config["selector"]
                attr = sel_config.get("attr", "text")
                get_all = sel_config.get("all", False)

                elements = response.css(selector)
                if not elements:
                    item[field] = [] if get_all else None
                    continue

                def _val(el):
                    if attr == "text":
                        return el.text.strip() if el.text else ""
                    elif attr == "html":
                        return el.html
                    return el.attrib.get(attr, "")

                if get_all:
                    item[field] = [_val(el) for el in elements]
                else:
                    item[field] = _val(elements[0])

            yield item

        # Follow links if configured
        if self._follow_links:
            links = response.css(self._follow_links)
            for link in links:
                href = link.attrib.get("href", "")
                if not href or href.startswith(("#", "javascript:", "mailto:")):
                    continue

                if self._follow_pattern and not self._follow_pattern.search(href):
                    continue

                if self._max_pages and self._pages_crawled >= self._max_pages:
                    break

                yield response.follow(href)


def run_spider(config, output_dir="output"):
    """Run a GenericSpider from config and save results.

    Args:
        config: Spider configuration dict.
        output_dir: Directory for output files.

    Returns:
        CrawlResult with stats and items.
    """
    spider = GenericSpider(config, output_dir=output_dir)
    result = spider.start()

    # Save results
    output_config = config.get("output", {"format": "jsonl"})
    fmt = output_config.get("format", "jsonl")
    filename = output_config.get("file", f"{config['name']}.{fmt}")
    filepath = Path(output_dir) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        result.items.to_json(str(filepath), indent=True)
    elif fmt == "jsonl":
        result.items.to_jsonl(str(filepath))
    else:
        # CSV fallback
        import csv
        if result.items:
            keys = list(result.items[0].keys())
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(result.items)

    log.info(f"Spider '{config['name']}' done — {result.stats.items_scraped} items, "
             f"{result.stats.requests_count} requests in {result.stats.elapsed_seconds:.1f}s")

    return result
