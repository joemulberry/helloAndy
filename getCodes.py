#!/usr/bin/env python3
"""
getCodes.py

Fetches a FIFA endpoint and builds a country→code mapping.
Writes a CSV-style text file `country_codes.txt` with lines formatted as: Country,Code

- Supports both the match-window endpoint and the FIFA Rankings structure like:
  {
      "rankings": [
          {
              "rankingItem": {
                  "name": "Argentina",
                  "countryCode": "ARG",
                  ...
              }
          }
      ]
  }
- Heuristically scans the JSON for (name, 3-letter code) pairs across common keys.
"""

import json
import re
import sys
from collections import OrderedDict
import argparse

try:
    import requests
except Exception:
    print("This script requires the 'requests' package. Install with: pip install requests", file=sys.stderr)
    raise

URL = (
    "https://inside.fifa.com/api/ranking-overview"
    "?locale=en&dateId=id14800&rankingType=football"
)

# Keys that commonly hold a readable country/team/association name
NAME_KEYS = {
    "country", "countryName", "associationName", "teamName", "name", "fifaName", "officialName", "displayName"
}

# Keys that commonly hold a 3-letter code
CODE_KEYS = {
    "code", "countryCode", "countryAbbreviation", "trigram", "abbreviation", "abbr", "fifaTrigramme"
}

TRIGRAM_RE = re.compile(r"^[A-Z]{3}$")


def extract_code_from_string(s: str) -> str | None:
    """Try to pull a 3-letter code from things like flag/src URLs or countryURL paths.
    Examples:
      https://api.fifa.com/api/v3/picture/flags-sq-2/ARG  -> ARG
      /fifa-world-ranking/ARG                             -> ARG
    """
    if not isinstance(s, str):
        return None
    # Look for /XXX at end of string or before query/fragment
    m = re.search(r"/([A-Z]{3})(?:[/?#].*)?$", s)
    if m:
        return m.group(1)
    # Fallback: plain 3-letter uppercase token
    if TRIGRAM_RE.match(s):
        return s
    return None


def looks_like_country_name(s: str) -> bool:
    return isinstance(s, str) and any(c.isalpha() for c in s) and len(s.strip()) >= 3


def looks_like_code(s: str) -> bool:
    return isinstance(s, str) and TRIGRAM_RE.match(s.upper() if s else "") is not None


def walk(obj):
    """Yield all dicts and lists recursively."""
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from walk(item)


def normalize_country_name(name: str) -> str:
    name = (name or "").strip()
    replacements = {
        "Korea Republic": "South Korea",
        "Korea DPR": "North Korea",
        "IR Iran": "Iran",
        "USA": "United States",
        "Türkiye": "Turkey",
        "Côte d’Ivoire": "Cote d'Ivoire",
        "Côte d'Ivoire": "Cote d'Ivoire",
    }
    return replacements.get(name, name)


def extract_pairs(payload) -> dict:
    pairs = {}

    # First: handle the specific FIFA Rankings structure shown by the user
    # payload = { "rankings": [ { "rankingItem": { "name": ..., "countryCode": ... } }, ... ] }
    try:
        rankings = payload.get("rankings")
        if isinstance(rankings, list):
            for entry in rankings:
                item = entry.get("rankingItem") if isinstance(entry, dict) else None
                if isinstance(item, dict):
                    n = item.get("name")
                    c = item.get("countryCode")
                    if looks_like_country_name(n) and looks_like_code(str(c)):
                        pairs.setdefault(normalize_country_name(str(n)), str(c).upper())
    except Exception:
        # Fall back to heuristic walker below
        pass

    # If we already found pairs from rankings, keep them and still walk the rest
    # to catch any additional (name, code) pairs present elsewhere in the payload.

    for node in walk(payload):
        if not isinstance(node, dict):
            continue

        # 1) Try to find name/code in the same dict via preferred keys
        name_val = None
        code_val = None

        for nk in NAME_KEYS:
            if nk in node and looks_like_country_name(node[nk]):
                name_val = node[nk]
                break

        for ck in CODE_KEYS:
            if ck in node and looks_like_code(str(node[ck])):
                code_val = str(node[ck]).upper()
                break

        # 2) Fallback: any "*name" and "*code/abbr/trigram" patterns
        if name_val is None:
            for k, v in node.items():
                if isinstance(k, str) and k.lower().endswith("name") and looks_like_country_name(v):
                    name_val = v
                    break

        if code_val is None:
            for k, v in node.items():
                if not isinstance(k, str):
                    continue
                key = k.lower()
                if (key.endswith("code") or key.endswith("abbr") or key.endswith("abbreviation") or key.endswith("trigram")) and looks_like_code(str(v)):
                    code_val = str(v).upper()
                    break

        if name_val and code_val:
            pairs.setdefault(normalize_country_name(str(name_val)), code_val)

        # 2b) Flag URL / countryURL extraction if still missing
        if not code_val:
            # flag.src often ends with /ARG
            flag = node.get("flag") if isinstance(node, dict) else None
            if isinstance(flag, dict):
                code_from_flag = extract_code_from_string(flag.get("src"))
                if code_from_flag:
                    code_val = code_from_flag
                    # use flag.title or flag.alt or existing name_val
                    if not name_val:
                        for cand in (flag.get("title"), flag.get("alt")):
                            if looks_like_country_name(cand):
                                name_val = cand
                                break

        if not code_val and isinstance(node, dict) and "countryURL" in node:
            code_from_url = extract_code_from_string(node.get("countryURL"))
            if code_from_url:
                code_val = code_from_url

        if name_val and code_val:
            pairs.setdefault(normalize_country_name(str(name_val)), str(code_val).upper())

        # 3) Some structures keep team under nested keys
        for side in ("homeTeam", "awayTeam", "team", "association"):
            sub = node.get(side)
            if isinstance(sub, dict):
                n = None
                c = None
                for nk in NAME_KEYS:
                    if nk in sub and looks_like_country_name(sub[nk]):
                        n = sub[nk]
                        break
                for ck in CODE_KEYS:
                    if ck in sub and looks_like_code(str(sub[ck])):
                        c = str(sub[ck]).upper()
                        break
                # Fallbacks from nested structures
                if not c and isinstance(sub, dict):
                    flag = sub.get("flag") if isinstance(sub.get("flag"), dict) else None
                    if flag:
                        c = extract_code_from_string(flag.get("src")) or c
                        if not n:
                            for cand in (flag.get("title"), flag.get("alt")):
                                if looks_like_country_name(cand):
                                    n = cand
                                    break
                    if not c and isinstance(sub.get("countryURL"), str):
                        c = extract_code_from_string(sub.get("countryURL")) or c

                if n and c:
                    pairs.setdefault(normalize_country_name(str(n)), str(c).upper())

    return pairs


def main():
    parser = argparse.ArgumentParser(description="Build Country,Code mapping from FIFA JSON")
    parser.add_argument("--url", default=URL, help="Endpoint to fetch (default: match-window)")
    args = parser.parse_args()
    fetch_url = args.url

    print(f"Fetching: {fetch_url}", file=sys.stderr)
    resp = requests.get(
        fetch_url,
        headers={
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "country-code-builder/1.0",
        },
        timeout=30,
    )
    resp.raise_for_status()
    try:
        data = resp.json()
    except json.JSONDecodeError:
        print("Error: Response was not valid JSON.", file=sys.stderr)
        sys.exit(1)

    mapping = extract_pairs(data)

    if not mapping:
        print("Warning: No (Country, Code) pairs were detected. The JSON structure may have changed.", file=sys.stderr)

    ordered = OrderedDict(sorted(mapping.items(), key=lambda kv: kv[0].lower()))

    out_path = "country_codes.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        for country, code in ordered.items():
            f.write(f"{country},{code}\n")

    print(f"Wrote {len(ordered)} (Country,Code) lines to {out_path}")


if __name__ == "__main__":
    main()