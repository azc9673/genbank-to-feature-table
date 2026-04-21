import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from Bio import SeqIO

INSDC_FEATURE_TABLE_URL = "https://www.insdc.org/submitting-standards/feature-table/"
REQUEST_TIMEOUT_SECONDS = 20
MIN_FEATURE_COUNT = 10
MIN_QUALIFIER_COUNT = 10
CACHE_FILE = Path(__file__).with_name(".insdc_feature_table_cache.json")


def extract_allowed_features_and_qualifiers(page_text):
    allowed_features = set()
    allowed_qualifiers = set()

    for raw_line in page_text.splitlines():
        line = raw_line.strip()

        if line.startswith("Feature Key"):
            feature_key = line.split("Feature Key", 1)[1].strip()
            if feature_key:
                allowed_features.add(feature_key)
        elif line.startswith("Qualifier"):
            qualifier_key = line.split("Qualifier", 1)[1].strip().lstrip("/").split("=", 1)[0]
            if qualifier_key:
                allowed_qualifiers.add(qualifier_key)

    return allowed_features, allowed_qualifiers


def validate_allowed_data(allowed_features, allowed_qualifiers):
    errors = []

    if len(allowed_features) < MIN_FEATURE_COUNT:
        errors.append(
            f"found only {len(allowed_features)} features; expected at least {MIN_FEATURE_COUNT}"
        )
    if len(allowed_qualifiers) < MIN_QUALIFIER_COUNT:
        errors.append(
            f"found only {len(allowed_qualifiers)} qualifiers; expected at least {MIN_QUALIFIER_COUNT}"
        )

    return not errors, "; ".join(errors)


def save_cache(cache_path, allowed_features, allowed_qualifiers):
    payload = {
        "saved_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_url": INSDC_FEATURE_TABLE_URL,
        "allowed_features": sorted(allowed_features),
        "allowed_qualifiers": sorted(allowed_qualifiers),
    }

    try:
        with cache_path.open("w", encoding="utf-8") as cache_file:
            json.dump(payload, cache_file, indent=2)
    except OSError as exc:
        print(f"Warning: could not update cache file {cache_path.name}: {exc}")


def load_cache(cache_path):
    if not cache_path.exists():
        return None

    try:
        with cache_path.open("r", encoding="utf-8") as cache_file:
            payload = json.load(cache_file)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Warning: could not read cache file {cache_path.name}: {exc}")
        return None

    allowed_features = set(payload.get("allowed_features", []))
    allowed_qualifiers = set(payload.get("allowed_qualifiers", []))
    saved_at_utc = payload.get("saved_at_utc", "unknown time")
    return allowed_features, allowed_qualifiers, saved_at_utc


def fetch_allowed_features_and_qualifiers(url, cache_path=CACHE_FILE):
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as exc:
        cached_data = load_cache(cache_path)
        if cached_data is not None:
            allowed_features, allowed_qualifiers, saved_at_utc = cached_data
            is_valid, validation_message = validate_allowed_data(
                allowed_features, allowed_qualifiers
            )
            if is_valid:
                print(
                    "Live INSDC fetch failed; using cached feature table "
                    f"from {saved_at_utc}. Reason: {exc}"
                )
                return allowed_features, allowed_qualifiers
            print(
                "Cached INSDC feature table was present but invalid: "
                f"{validation_message}"
            )

        print(f"Failed to fetch the current INSDC feature table: {exc}")
        sys.exit(1)

    soup = BeautifulSoup(response.text, "html.parser")
    page_text = soup.get_text("\n")
    allowed_features, allowed_qualifiers = extract_allowed_features_and_qualifiers(page_text)
    is_valid, validation_message = validate_allowed_data(
        allowed_features, allowed_qualifiers
    )

    if not is_valid:
        cached_data = load_cache(cache_path)
        if cached_data is not None:
            cached_features, cached_qualifiers, saved_at_utc = cached_data
            cache_is_valid, cache_validation_message = validate_allowed_data(
                cached_features, cached_qualifiers
            )
            if cache_is_valid:
                print(
                    "Live INSDC scrape returned incomplete data; using cached feature table "
                    f"from {saved_at_utc}. Reason: {validation_message}"
                )
                return cached_features, cached_qualifiers
            print(
                "Cached INSDC feature table was present but invalid: "
                f"{cache_validation_message}"
            )

        print(f"Failed to validate live INSDC feature table data: {validation_message}")
        sys.exit(1)

    save_cache(cache_path, allowed_features, allowed_qualifiers)
    print(
        "Fetched current INSDC feature table "
        f"({len(allowed_features)} features, {len(allowed_qualifiers)} qualifiers)."
    )
    return allowed_features, allowed_qualifiers

def format_location(location):
    start = location.start + 1
    end = location.end
    strand = location.strand
    
    if isinstance(location.start, int) and isinstance(location.end, int):
        return f"{start}\t{end}"
    else:
        start_str = f"<{start}" if location.start_is_partial else f"{start}"
        end_str = f">{end}" if location.end_is_partial else f"{end}"
        return f"{start_str}\t{end_str}"

def parse_genbank_to_tab(input_file, output_file, allowed_features, allowed_qualifiers):
    with open(output_file, 'w') as out_f:
        for record in SeqIO.parse(input_file, "genbank"):
            seq_id = record.id
            out_f.write(f">Feature {seq_id}\n")
            
            for feature in record.features:
                if feature.type not in allowed_features:
                    continue
                
                # Handle feature locations
                if len(feature.location.parts) > 1:
                    for i, part in enumerate(feature.location.parts):
                        if i == 0:
                            out_f.write(f"{format_location(part)}\t{feature.type}\t\t\n")
                        else:
                            out_f.write(f"{format_location(part)}\t\t\t\t\n")
                else:
                    out_f.write(f"{format_location(feature.location)}\t{feature.type}\t\t\n")

                # Write the qualifiers
                for qualifier_key, qualifier_value in feature.qualifiers.items():
                    if qualifier_key not in allowed_qualifiers:
                        continue
                    if isinstance(qualifier_value, list):
                        for value in qualifier_value:
                            out_f.write(f"\t\t\t{qualifier_key}\t{value}\n")
                    else:
                        out_f.write(f"\t\t\t{qualifier_key}\t{qualifier_value}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python converter-script.py <input_genbank_file> <output_tab_file>")
        sys.exit(1)

    input_genbank_file = sys.argv[1]
    output_tab_file = sys.argv[2]
    
    allowed_features, allowed_qualifiers = fetch_allowed_features_and_qualifiers(
        INSDC_FEATURE_TABLE_URL
    )

    parse_genbank_to_tab(input_genbank_file, output_tab_file, allowed_features, allowed_qualifiers)
    print(f"Conversion complete. Output written to {output_tab_file}")
