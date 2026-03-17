# ingestion/fetch_physicians_api.py
from pathlib import Path
import sys
import time
import requests
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# PASTE YOUR EXACT CMS API URL HERE
API_URL = "https://data.cms.gov/data-api/v1/dataset/8889d81e-2ee7-448f-8713-f071038289b5/data"

OUTPUT_FILE = DATA_DIR / "physicians_api_data.csv"
PAGE_SIZE = 5000
REQUEST_TIMEOUT = 60
SLEEP_BETWEEN_CALLS = 0.2


def say(message: str) -> None:
    print(f"[INFO] {message}")


def warn(message: str) -> None:
    print(f"[WARN] {message}")


def fail(message: str) -> None:
    print(f"[ERROR] {message}")


def validate_config() -> None:
    say("Checking script configuration...")

    if "PASTE_COPIED_CMS_PHYSICIAN_API_URL_HERE" in API_URL:
        raise ValueError(
            "You still need to paste the copied CMS API URL into API_URL."
        )

    if not API_URL.startswith("https://"):
        raise ValueError("API_URL must start with https://")

    say(f"API URL looks present: {API_URL}")
    say(f"Output file will be: {OUTPUT_FILE}")
    say(f"Page size is set to: {PAGE_SIZE}")


def try_fetch_stats(api_url: str) -> int | None:
    stats_url = f"{api_url}/stats"
    say("Trying stats endpoint so we know the expected row count...")
    say(f"Stats URL: {stats_url}")

    try:
        response = requests.get(stats_url, timeout=REQUEST_TIMEOUT)
        say(f"Stats response status: {response.status_code}")
        response.raise_for_status()

        payload = response.json()
        total_rows = payload.get("total_rows")

        if total_rows is None:
            warn("Stats endpoint responded, but no total_rows field was found.")
            return None

        say(f"Stats says expected total rows = {total_rows}")
        return total_rows

    except Exception as exc:
        warn(f"Could not read stats endpoint: {exc}")
        warn("This is not fatal. The main data pull will still continue.")
        return None


def fetch_all_rows(api_url: str) -> list[dict]:
    say("Starting paginated API extraction...")

    offset = 0
    page_number = 1
    all_rows: list[dict] = []

    while True:
        params = {
            "size": PAGE_SIZE,
            "offset": offset,
        }

        say("-" * 60)
        say(f"Requesting page {page_number}")
        say(f"Offset: {offset}")
        say(f"Params: {params}")

        try:
            response = requests.get(api_url, params=params, timeout=REQUEST_TIMEOUT)
            say(f"Response status code: {response.status_code}")
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            fail(f"HTTP error on page {page_number}: {exc}")
            fail(f"Response text preview: {response.text[:500]}")
            raise
        except requests.exceptions.Timeout as exc:
            fail(f"Timeout on page {page_number}: {exc}")
            raise
        except requests.exceptions.RequestException as exc:
            fail(f"Request exception on page {page_number}: {exc}")
            raise

        try:
            batch = response.json()
        except ValueError as exc:
            fail(f"Could not parse JSON on page {page_number}: {exc}")
            fail(f"Raw response preview: {response.text[:500]}")
            raise

        if not isinstance(batch, list):
            fail("Expected the API to return a list of rows, but it returned something else.")
            fail(f"Returned Python type: {type(batch)}")
            fail(f"Returned content preview: {str(batch)[:500]}")
            raise ValueError("API response was not a list.")

        batch_count = len(batch)
        say(f"Rows returned on this page: {batch_count}")

        if batch_count == 0:
            say("No rows returned. Pagination is complete.")
            break

        all_rows.extend(batch)
        say(f"Running total rows collected: {len(all_rows)}")

        if batch_count < PAGE_SIZE:
            say(
                "This page returned fewer rows than PAGE_SIZE, so this looks like the final page."
            )
            break

        offset += PAGE_SIZE
        page_number += 1

        say(f"Sleeping {SLEEP_BETWEEN_CALLS} seconds before next request...")
        time.sleep(SLEEP_BETWEEN_CALLS)

    say("Finished pulling all available rows from the API.")
    return all_rows


def save_rows_to_csv(rows: list[dict], output_file: Path) -> None:
    say("Converting API rows into a pandas DataFrame...")
    df = pd.DataFrame(rows)

    say(f"DataFrame shape: {df.shape}")

    if df.empty:
        warn("The DataFrame is empty. A CSV will still be written, but it will have no rows.")
    else:
        say("Preview of first 5 rows:")
        print(df.head())

        say("Preview of column names:")
        print(df.columns.tolist())

    say(f"Writing CSV to disk: {output_file}")
    df.to_csv(output_file, index=False)
    say("CSV write complete.")

    if output_file.exists():
        say(f"Confirmed file exists: {output_file}")
        say(f"File size in bytes: {output_file.stat().st_size}")
    else:
        raise FileNotFoundError(f"Expected output file was not found after writing: {output_file}")


def main() -> None:
    say("Physicians API extraction script started.")

    try:
        validate_config()

        expected_total = try_fetch_stats(API_URL)
        rows = fetch_all_rows(API_URL)

        say(f"Total rows fetched from API: {len(rows)}")

        if expected_total is not None:
            if len(rows) == expected_total:
                say("Fetched row count matches the stats endpoint total.")
            else:
                warn(
                    f"Fetched row count ({len(rows)}) does NOT match stats total ({expected_total})."
                )
                warn("This may be normal if the API or stats endpoint changed, but it should be checked.")

        save_rows_to_csv(rows, OUTPUT_FILE)

        say("Script completed successfully.")
        say("Next step: validate the downloaded file before loading it into your warehouse.")

    except Exception as exc:
        fail("The script stopped because of an exception.")
        fail(f"Exception type: {type(exc).__name__}")
        fail(f"Exception message: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()