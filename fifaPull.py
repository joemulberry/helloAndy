import pandas as pd
import requests

def fetch_fifa_rankings_timeseries(country: str, gender: int = 1, locale: str = "en") -> pd.DataFrame:
    
    """
    First we must take the country text and find the country code 
    """
    print(country)
    # --- Load country→code map robustly ---
    import unicodedata as _ud
    import difflib as _difflib

    def _norm_name(s: str) -> str:
        # lowercase, trim, strip accents/diacritics so "Türkiye" → "turkiye"
        s = (s or "").strip().lower()
        s = _ud.normalize("NFKD", s)
        s = s.encode("ascii", "ignore").decode("ascii")
        return s

    RAW_COUNTRY_TO_CODE = {}
    NORM_COUNTRY_TO_CODE = {}

    with open("country_codes.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(",") if p.strip()]
            if len(parts) != 2:
                print(f"Skipping malformed line: {line!r}")
                continue
            country_name, code = parts[0], parts[1]
            code = code.strip().upper()
            RAW_COUNTRY_TO_CODE[country_name] = code
            NORM_COUNTRY_TO_CODE[_norm_name(country_name)] = code

    # Common aliases seen in FIFA data / general usage
    _ALIASES = {
        "ir iran": "iran",
        "korea republic": "south korea",
        "korea dpr": "north korea",
        "usa": "united states",
        "cote d’ivoire": "cote d'ivoire",
        "cote d'ivoire": "cote d'ivoire",
        "tuerkiye": "turkiye",  # if someone types with ue
    }

    query_norm = _norm_name(country)
    # Map alias if needed
    query_lookup = _ALIASES.get(query_norm, query_norm)
    country_code = NORM_COUNTRY_TO_CODE.get(query_lookup)

    if not country_code:
        # Try close matches to help the user diagnose issues
        candidates = list(NORM_COUNTRY_TO_CODE.keys())
        suggestions = _difflib.get_close_matches(query_norm, candidates, n=5, cutoff=0.6)
        raise ValueError(
            f"Unknown country '{country}'. Try one of: " + ", ".join(suggestions or sorted(RAW_COUNTRY_TO_CODE.keys())[:10])
        )

    print({"input": country, "resolved_code": country_code})
    """Fetch the full FIFA ranking time series for a given country.

    Args:
        country_code: FIFA 3-letter code e.g. "BRA", "ENG" (case-insensitive).
        gender: 1 for men, 2 for women (per inside.fifa.com API).
        locale: language locale string (default "en").
    Returns:
        A pandas DataFrame with columns like: date, rank, points, previousRank,
        confederationRank, name, countryCode; sorted by date ascending.
    """

    url = "https://inside.fifa.com/api/rankings/by-country"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/139.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://inside.fifa.com/fifa-world-ranking/BRA?gender=men",
        "Origin": "https://inside.fifa.com",
        "Connection": "keep-alive",
    }
    params = {
        "gender": int(gender),
        "countryCode": (country_code or "").strip().upper(),
        "locale": locale,
    }

    # Optional: forward browser cookies if you paste them into the env var FIFA_COOKIE (helps when behind Akamai)
    import os as _os
    _cookie_env = _os.environ.get("FIFA_COOKIE")
    if _cookie_env:
        headers["Cookie"] = _cookie_env

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=20)
    except requests.RequestException as e:
        raise

    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        raise

    try:
        data = resp.json() or {}
    except ValueError:
        raise

    items = []
    chosen_key = None
    if isinstance(data, list):
        items = data
        chosen_key = "__root_list__"
    elif isinstance(data, dict):
        for key in ("rankings", "rankingHistory", "data", "items", "results"):
            if isinstance(data.get(key), list):
                items = data.get(key)
                chosen_key = key
                break
        if not items:
            # Fallback: maybe the dict itself is the item
            items = [data]
            chosen_key = "__self_dict__"

    rows = []
    for entry in items:
        entry = entry or {}
        ri = entry.get("rankingItem", {}) if isinstance(entry, dict) else {}

        # Build a lower-cased key map for easy alt lookups
        lcentry = {str(k).lower(): v for k, v in (entry.items() if isinstance(entry, dict) else [])}
        lcri = {str(k).lower(): v for k, v in (ri.items() if isinstance(ri, dict) else [])}

        def first_non_null(*vals):
            for v in vals:
                if v is not None and v != "":
                    return v
            return None

        # Name extraction: prefer TeamName[Locale==locale] -> Description, else first Description, else ri/name
        def extract_name():
            tn = entry.get("TeamName")
            if isinstance(tn, list) and tn:
                # Try match locale exactly
                for t in tn:
                    if isinstance(t, dict) and t.get("Locale") == locale:
                        return t.get("Description") or t.get("Locale")
                # Fallback to first Description
                for t in tn:
                    if isinstance(t, dict) and t.get("Description"):
                        return t.get("Description")
            return first_non_null(
                ri.get("name"), entry.get("name"), lcri.get("name"), lcentry.get("name")
            )

        # Country code: IdCountry or countryCode fallbacks
        def extract_cc():
            return first_non_null(
                entry.get("IdCountry"), entry.get("countryCode"),
                lcentry.get("idcountry"), lcentry.get("countrycode"),
                params.get("countryCode")
            )

        # Date: PubDate > lastUpdateDate > date > PrePubDate
        def extract_date():
            return first_non_null(
                entry.get("PubDate"), entry.get("PrePubDate"), entry.get("EOYPubDate"),
                entry.get("lastUpdateDate"), entry.get("date"),
                lcentry.get("pubdate"), lcentry.get("prepubdate"), lcentry.get("eoypubdate"),
                lcentry.get("lastupdatedate"), lcentry.get("date"),
                ri.get("lastUpdateDate"), lcri.get("lastupdatedate")
            )

        # Rank and points (+ previous/confed)
        rank_val = first_non_null(
            entry.get("Rank"), lcentry.get("rank"), ri.get("rank"), lcri.get("rank")
        )
        points_val = first_non_null(
            entry.get("TotalPoints"), lcentry.get("totalpoints"),
            entry.get("DecimalTotalPoints"), lcentry.get("decimaltotalpoints"),
            ri.get("totalPoints"), lcri.get("totalpoints")
        )
        prev_rank_val = first_non_null(
            entry.get("PrevRank"), lcentry.get("prevrank"), ri.get("previousRank"), lcri.get("previousrank")
        )
        confed_rank_val = first_non_null(
            entry.get("ConfederationRank"), lcentry.get("confederationrank"),
            ri.get("confederationRank"), lcri.get("confederationrank")
        )

        row = {
            "date": extract_date(),
            "rank": rank_val,
            "points": points_val,
            "previousRank": prev_rank_val,
            "confederationRank": confed_rank_val,
            "name": extract_name(),
            "countryCode": extract_cc(),
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    if not df.empty and "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.sort_values("date").reset_index(drop=True)
        import pandas as _pd
        # Ensure timezone-aware datetimes in UTC for safe comparison
        if df["date"].dt.tz is None:
            df["date"] = df["date"].dt.tz_localize("UTC")
        else:
            df["date"] = df["date"].dt.tz_convert("UTC")
        cutoff_date = _pd.Timestamp.now(tz="UTC") - _pd.DateOffset(months=30)
        df = df[df["date"] >= cutoff_date].reset_index(drop=True)

        # Coerce numeric columns where possible
        for col in ("rank", "points", "previousRank", "confederationRank"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def average_rank(df: pd.DataFrame) -> float:
    """Return the average rank from the trimmed DataFrame."""
    if df.empty or "rank" not in df.columns:
        return float("nan")
    return df["rank"].mean(skipna=True)

# Tip: to mirror your browser session if needed, export your cookies first, e.g.:
# import os; os.environ["FIFA_COOKIE"] = "OptanonAlertBoxClosed=...; ak_bmsc=...; bm_sv=...; _abck=..."

# x = fetch_fifa_rankings_timeseries('spain')
# print(x)
# print('finland', "Average rank (last 30 months):", average_rank(x))