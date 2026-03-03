"""
Moteur de scraping core — wraps all Scrapling fetcher modes.

Modes:
  - basic:   HTTP via curl_cffi (Fetcher.get/post)
  - dynamic: Playwright/Chromium (DynamicFetcher.fetch)
  - stealth: Anti-detection Chromium (StealthyFetcher.fetch)
"""

import csv
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

from scrapling import Fetcher, DynamicFetcher, StealthyFetcher

log = logging.getLogger("scraper")


def fetch_page(url, mode="basic", method="GET", **kwargs):
    """Fetch a single page using the specified mode.

    Args:
        url: Target URL.
        mode: "basic", "dynamic", or "stealth".
        method: HTTP method (only for basic mode).
        **kwargs: Passed directly to the fetcher.

    Returns:
        Scrapling Response object.
    """
    if mode == "basic":
        fn = getattr(Fetcher, method.lower())
        return fn(url, **kwargs)
    elif mode == "dynamic":
        return DynamicFetcher.fetch(url, **kwargs)
    elif mode == "stealth":
        return StealthyFetcher.fetch(url, **kwargs)
    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'basic', 'dynamic', or 'stealth'.")


def extract_data(response, selectors):
    """Extract data from a Response using CSS selectors.

    Args:
        response: Scrapling Response object.
        selectors: Dict mapping field names to CSS selectors.
            Each selector can be:
              - A string: "h1" -> first match text
              - A dict with keys:
                  selector: CSS selector string
                  attr: attribute to extract (default: text)
                  all: bool, return all matches (default: false)

    Returns:
        Dict of extracted data.
    """
    data = {"_url": response.url, "_status": response.status}

    for field, sel_config in selectors.items():
        if isinstance(sel_config, str):
            sel_config = {"selector": sel_config}

        selector = sel_config["selector"]
        attr = sel_config.get("attr", "text")
        get_all = sel_config.get("all", False)

        elements = response.css(selector)

        if not elements:
            data[field] = [] if get_all else None
            continue

        def _extract_value(el):
            if attr == "text":
                return el.text.strip() if el.text else ""
            elif attr == "html":
                return el.html
            else:
                return el.attrib.get(attr, "")

        if get_all:
            data[field] = [_extract_value(el) for el in elements]
        else:
            data[field] = _extract_value(elements[0])

    return data


def run_job(job_config, output_dir="output"):
    """Execute a single scraping job from config.

    Args:
        job_config: Dict with keys: name, url/urls, mode, selectors, options, output.
        output_dir: Base directory for output files.

    Returns:
        List of extracted data dicts.
    """
    name = job_config["name"]
    urls = job_config.get("urls", [])
    if not urls and "url" in job_config:
        urls = [job_config["url"]]

    mode = job_config.get("mode", "basic")
    method = job_config.get("method", "GET")
    selectors = job_config.get("selectors", {})
    options = job_config.get("options", {})
    output_config = job_config.get("output", {})

    log.info(f"[{name}] Starting — {len(urls)} URL(s), mode={mode}")

    results = []
    for url in urls:
        try:
            log.info(f"[{name}] Fetching {url}")
            response = fetch_page(url, mode=mode, method=method, **options)
            if selectors:
                data = extract_data(response, selectors)
            else:
                data = {
                    "_url": response.url,
                    "_status": response.status,
                    "_title": response.css("title")[0].text if response.css("title") else "",
                    "_text": response.text[:500] if hasattr(response, "text") else "",
                }
            results.append(data)
            log.info(f"[{name}] OK {url} — status {response.status}")
        except Exception as e:
            log.error(f"[{name}] FAILED {url} — {e}")
            results.append({"_url": url, "_error": str(e)})

    if results and output_config:
        save_results(results, output_config, output_dir, name)

    return results


def save_results(results, output_config, output_dir="output", job_name="results"):
    """Save extracted data to file.

    Args:
        results: List of dicts.
        output_config: Dict with keys: format (json/jsonl/csv), file (optional).
        output_dir: Base output directory.
        job_name: Used as default filename.
    """
    fmt = output_config.get("format", "json")
    filename = output_config.get("file", f"{job_name}.{fmt}")
    filepath = Path(output_dir) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        filepath.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    elif fmt == "jsonl":
        with open(filepath, "w", encoding="utf-8") as f:
            for item in results:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
    elif fmt == "csv":
        if results:
            keys = list(results[0].keys())
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(results)
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'json', 'jsonl', or 'csv'.")

    log.info(f"Saved {len(results)} results to {filepath}")
    return filepath
