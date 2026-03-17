from pathlib import Path

import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas


BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
SOURCE_DIR = BASE_DIR / "data_sources"

PHYSICIANS_FILE = DATA_DIR / "physicians_api_data.csv"
READMISSIONS_FILE = SOURCE_DIR / "FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv"
HCAHPS_FILE = SOURCE_DIR / "HCAHPS-Hospital.csv"


def log(message: str) -> None:
    print(f"[INFO] {message}")


def check_file_exists(file_path: Path, label: str) -> None:
    log(f"Checking {label} file at: {file_path}")

    if not file_path.exists():
        raise FileNotFoundError(f"{label} file not found: {file_path}")

    log(f"{label} file found.")


def connect_to_snowflake():
    log("Connecting to Snowflake...")

    conn = snowflake.connector.connect(
        user="ROSCOEDELA",
        password="ErinJonesFrankJones95!",
        account="QQQVDBF-XC19320",
        warehouse="COMPUTE_WH",
        database="HEALTHCARE_DB",
        schema="RAW",
    )

    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_VERSION()")
    version = cursor.fetchone()[0]
    cursor.close()

    log(f"Connected to Snowflake version: {version}")
    log("Snowflake connection established.")
    return conn


def bulk_load_dataframe(conn, df: pd.DataFrame, table_name: str) -> None:
    log(f"Starting bulk load for table: {table_name}")
    log(f"DataFrame shape: {df.shape}")

    success, nchunks, nrows, _ = write_pandas(
        conn=conn,
        df=df,
        table_name=table_name,
        auto_create_table=True,
        overwrite=True,
    )

    if not success:
        raise RuntimeError(f"Bulk load failed for table: {table_name}")

    log(f"Bulk load finished for table: {table_name}")
    log(f"Chunks loaded: {nchunks}")
    log(f"Rows loaded: {nrows}")


def read_physicians() -> pd.DataFrame:
    log("Reading physicians dataset...")
    df = pd.read_csv(PHYSICIANS_FILE, low_memory=False)
    log(f"Physicians rows: {len(df)}")
    log(f"Physicians columns: {len(df.columns)}")
    return df


def read_readmissions() -> pd.DataFrame:
    log("Reading readmissions dataset...")
    df = pd.read_csv(READMISSIONS_FILE, low_memory=False)
    log(f"Readmissions rows: {len(df)}")
    log(f"Readmissions columns: {len(df.columns)}")
    return df


def read_hcahps() -> pd.DataFrame:
    log("Reading HCAHPS dataset...")
    df = pd.read_csv(HCAHPS_FILE, low_memory=False)
    log(f"HCAHPS rows: {len(df)}")
    log(f"HCAHPS columns: {len(df.columns)}")
    return df


def main() -> None:
    log("Starting raw data bulk load process...")

    check_file_exists(PHYSICIANS_FILE, "Physicians")
    check_file_exists(READMISSIONS_FILE, "Readmissions")
    check_file_exists(HCAHPS_FILE, "HCAHPS")

    conn = connect_to_snowflake()

    try:
        physicians_df = read_physicians()
        readmissions_df = read_readmissions()
        hcahps_df = read_hcahps()

        bulk_load_dataframe(conn, physicians_df, "RAW_PHYSICIANS")
        bulk_load_dataframe(conn, readmissions_df, "RAW_READMISSIONS")
        bulk_load_dataframe(conn, hcahps_df, "RAW_HCAHPS")

        log("All raw tables loaded successfully.")

    finally:
        conn.close()
        log("Snowflake connection closed.")


if __name__ == "__main__":
    main()