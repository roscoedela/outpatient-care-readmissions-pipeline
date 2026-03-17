from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
SOURCE_DIR = BASE_DIR / "data_sources"

physicians_file = DATA_DIR / "physicians_api_data.csv"
readmissions_file = SOURCE_DIR / "FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv"
hcahps_file = SOURCE_DIR / "HCAHPS-Hospital.csv"


def validate_physicians() -> None:
    print("\nValidating physicians dataset...")
    df = pd.read_csv(physicians_file, low_memory=False)

    print(f"Row count: {len(df)}")

    null_npi_count = df["Rndrng_NPI"].isnull().sum()
    duplicate_npi_count = df["Rndrng_NPI"].duplicated().sum()

    if null_npi_count == 0:
        print("PASS: Rndrng_NPI contains no null values.")
    else:
        print(f"FAIL: Rndrng_NPI contains {null_npi_count} null values.")

    if duplicate_npi_count == 0:
        print("PASS: Rndrng_NPI values are unique.")
    else:
        print(f"FAIL: Found {duplicate_npi_count} duplicate Rndrng_NPI values.")


def validate_readmissions() -> None:
    print("\nValidating readmissions dataset...")
    df = pd.read_csv(readmissions_file, low_memory=False)

    print(f"Row count: {len(df)}")

    null_facility_id_count = df["Facility ID"].isnull().sum()

    readmission_ratio = pd.to_numeric(
        df["Excess Readmission Ratio"],
        errors="coerce"
    )

    invalid_ratio_count = ((readmission_ratio <= 0) & readmission_ratio.notna()).sum()

    if null_facility_id_count == 0:
        print("PASS: Facility ID contains no null values.")
    else:
        print(f"FAIL: Facility ID contains {null_facility_id_count} null values.")

    if invalid_ratio_count == 0:
        print("PASS: Excess Readmission Ratio values are greater than 0 where present.")
    else:
        print(f"FAIL: Found {invalid_ratio_count} invalid Excess Readmission Ratio values.")


def validate_hcahps() -> None:
    print("\nValidating HCAHPS dataset...")
    df = pd.read_csv(hcahps_file, low_memory=False)

    print(f"Row count: {len(df)}")

    null_facility_id_count = df["Facility ID"].isnull().sum()

    survey_response_rate = pd.to_numeric(
        df["Survey Response Rate Percent"],
        errors="coerce"
    )

    invalid_response_rate_count = (
        ((survey_response_rate < 0) | (survey_response_rate > 100))
        & survey_response_rate.notna()
    ).sum()

    non_numeric_response_rate_count = survey_response_rate.isna().sum()

    if null_facility_id_count == 0:
        print("PASS: Facility ID contains no null values.")
    else:
        print(f"FAIL: Facility ID contains {null_facility_id_count} null values.")

    if invalid_response_rate_count == 0:
        print("PASS: Survey Response Rate Percent values are within 0 to 100 where present.")
    else:
        print(
            f"FAIL: Found {invalid_response_rate_count} Survey Response Rate Percent values outside 0 to 100."
        )

    print(
        f"INFO: Survey Response Rate Percent has {non_numeric_response_rate_count} non-numeric or missing values after coercion."
    )


if __name__ == "__main__":
    validate_physicians()
    validate_readmissions()
    validate_hcahps()