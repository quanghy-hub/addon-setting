#!/usr/bin/env python3
"""
compile_filters.py - Consolidated uBlock Origin Filter Compiler
Downloads, deduplicates, and compiles multiple adblock lists into a single optimized file.
Designed for 0-cloud overhead, runnable locally or via GitHub Actions.
"""

from __future__ import annotations

import concurrent.futures
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Tuple

REPO_DIR = Path(__file__).resolve().parent.parent
CUSTOM_FILTERS_FILE = REPO_DIR / "filters.txt"
OUTPUT_ALL_IN_ONE = REPO_DIR / "filters_all_in_one.txt"

# Upstream Filter Sources matching user's uBlock Origin profile
SOURCES = [
    # 1. uBlock Base Assets
    ("uBlock Filters", "https://ublockorigin.github.io/uAssets/filters/filters.txt"),
    ("uBlock Badware", "https://ublockorigin.github.io/uAssets/filters/badware.txt"),
    ("uBlock Privacy", "https://ublockorigin.github.io/uAssets/filters/privacy.txt"),
    ("uBlock Quick Fixes", "https://ublockorigin.github.io/uAssets/filters/quick-fixes.txt"),
    ("uBlock Unbreak", "https://ublockorigin.github.io/uAssets/filters/unbreak.txt"),
    # 2. Ads (EasyList + AdGuard Ads without EasyList)
    ("EasyList", "https://ublockorigin.github.io/uAssets/thirdparties/easylist.txt"),
    ("AdGuard Ads (No-EasyList)", "https://filters.adtidy.org/extension/ublock/filters/2_without_easylist.txt"),
    # 3. Privacy (EasyPrivacy + URL Tracking)
    ("EasyPrivacy", "https://ublockorigin.github.io/uAssets/thirdparties/easyprivacy.txt"),
    ("uBO URL Tracking", "https://ublockorigin.github.io/uAssets/filters/privacy-removeparam.txt"),
    # 4. Malware & Security
    ("Online Malicious URL", "https://malware-filter.pages.dev/urlhaus-filter-ag-online.txt"),
    ("Peter Lowe Ad Servers", "https://pgl.yoyo.org/adservers/serverlist.php?hostformat=adblockplus&mimetype=plaintext"),
    # 5. Cookie & Annoyance Notices
    ("uBO Cookie Notices", "https://ublockorigin.github.io/uAssets/filters/annoyances-cookies.txt"),
    ("EasyList Cookie Notices", "https://ublockorigin.github.io/uAssets/thirdparties/easylist-cookies.txt"),
    ("AdGuard Cookie Notices", "https://filters.adtidy.org/extension/ublock/filters/18.txt"),
    # 6. Vietnam Local Ads (ABPVN)
    ("ABPVN Vietnam", "https://raw.githubusercontent.com/abpvn/abpvn/master/filter/abpvn.txt"),
]


def fetch_source(name: str, url: str) -> Tuple[str, List[str]]:
    """Fetches a single filter source and returns clean lines."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
            lines = raw.splitlines()
            return name, lines
    except Exception as e:
        print(f"[WARN] Failed to fetch '{name}' ({url}): {e}", file=sys.stderr)
        return name, []


def is_rule_line(line: str) -> bool:
    """Checks whether line is an actual active filter rule (not comment or section header)."""
    s = line.strip()
    if not s:
        return False
    if s.startswith("!"):
        # Check for special directives like !#if or !#include (rare, treat as non-rules)
        return False
    if s.startswith("[Adblock") or s.startswith("[AutoProxy"):
        return False
    return True


def compile_filters() -> Dict[str, int]:
    """Compiles all sources into a single deduplicated file."""
    start_time = time.perf_counter()
    print(">>> Starting filter collection and compilation...")

    # Load custom personal rules first
    custom_rules: List[str] = []
    if CUSTOM_FILTERS_FILE.exists():
        with open(CUSTOM_FILTERS_FILE, "r", encoding="utf-8") as f:
            custom_rules = f.read().splitlines()

    downloaded_sources: List[Tuple[str, List[str]]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_map = {
            executor.submit(fetch_source, name, url): name for name, url in SOURCES
        }
        for future in concurrent.futures.as_completed(future_map):
            name, lines = future.result()
            print(f"  + Fetched '{name}': {len(lines):,} lines")
            downloaded_sources.append((name, lines))

    # Deduplication Engine (Preserving insertion order)
    seen_rules: Set[str] = set()
    unique_rules: List[str] = []
    total_raw_rules = 0

    # 1. Add custom rules first (Highest priority)
    for line in custom_rules:
        s = line.strip()
        if is_rule_line(s):
            total_raw_rules += 1
            if s not in seen_rules:
                seen_rules.add(s)
                unique_rules.append(s)

    # 2. Add upstream sources
    for name, lines in downloaded_sources:
        for line in lines:
            s = line.strip()
            if is_rule_line(s):
                total_raw_rules += 1
                if s not in seen_rules:
                    seen_rules.add(s)
                    unique_rules.append(s)

    duplicates_removed = total_raw_rules - len(unique_rules)
    elapsed = time.perf_counter() - start_time

    # Categorize rules
    cosmetic_count = sum(1 for r in unique_rules if "##" in r or "#@#" in r or "#?#" in r)
    network_count = len(unique_rules) - cosmetic_count

    # Write output file
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    header = f"""! Title: All-in-One Consolidated uBlock Origin Filters (Deduplicated)
! Description: Merged EasyList, AdGuard, EasyPrivacy, uBlock, Malicious URL, Cookie Notices & Personal Rules.
! Updated: {now_utc}
! Total Rules: {len(unique_rules):,} (Network: {network_count:,}, Cosmetic: {cosmetic_count:,})
! Duplicates Eliminated: {duplicates_removed:,}
! Homepage: https://github.com/quanghy-hub/addon-setting
! Expires: 1 days
! ----------------------------------------------------------------------
"""

    with open(OUTPUT_ALL_IN_ONE, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        f.write("\n".join(unique_rules) + "\n")

    file_size_mb = OUTPUT_ALL_IN_ONE.stat().st_size / (1024 * 1024)

    stats = {
        "total_raw": total_raw_rules,
        "unique": len(unique_rules),
        "duplicates_removed": duplicates_removed,
        "network": network_count,
        "cosmetic": cosmetic_count,
        "size_mb": round(file_size_mb, 2),
        "elapsed_sec": round(elapsed, 2),
    }

    print("\n" + "=" * 60)
    print(">>> COMPILATION FINISHED SUCCESSFULLY!")
    print(f"  - Total Raw Rules Scanned:  {stats['total_raw']:,}")
    print(f"  - Duplicates Eliminated:    {stats['duplicates_removed']:,} (Giảm ~{(stats['duplicates_removed']/stats['total_raw']*100):.1f}%)")
    print(f"  - Final Unique Rules:       {stats['unique']:,}")
    print(f"    * Network Filters:        {stats['network']:,}")
    print(f"    * Cosmetic Filters:       {stats['cosmetic']:,}")
    print(f"  - Output File:              {OUTPUT_ALL_IN_ONE} ({stats['size_mb']} MB)")
    print(f"  - Processing Time:          {stats['elapsed_sec']} seconds")
    print("=" * 60 + "\n")

    return stats


if __name__ == "__main__":
    compile_filters()
