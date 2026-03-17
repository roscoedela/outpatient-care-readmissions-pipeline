import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

physicians = pd.read_csv(BASE_DIR / "Medicare_Physician_Other_Practitioners_by_Provider_2023.csv")
readmissions = pd.read_csv(BASE_DIR / "FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv")
hcahps = pd.read_csv(BASE_DIR / "HCAHPS-Hospital.csv")

print("Physicians")
print(physicians.head())
print(physicians.info())

print("\nReadmissions")
print(readmissions.head())
print(readmissions.info())

print("\nHCAHPS")
print(hcahps.head())
print(hcahps.info())

# row counts
print("\nROW COUNTS")
print(len(physicians))
print(len(readmissions))
print(len(hcahps))

# null analysis
print("\nNULL COUNTS — PHYSICIANS")
print(physicians.isnull().sum())

print("\nNULL COUNTS — READMISSIONS")
print(readmissions.isnull().sum())

print("\nNULL COUNTS — HCAHPS")
print(hcahps.isnull().sum())

print("\nUNIQUE STATES")
print(readmissions["State"].unique())

print("\nNUMERIC SUMMARY — READMISSIONS")
print(readmissions.describe())