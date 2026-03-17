select
    "Facility ID" as facility_id,
    "Facility Name" as facility_name,
    "State" as state_code,
    "Measure Name" as measure_name,
    "Number of Discharges" as number_of_discharges,
    "Footnote" as footnote,
    "Excess Readmission Ratio" as excess_readmission_ratio,
    "Predicted Readmission Rate" as predicted_readmission_rate,
    "Expected Readmission Rate" as expected_readmission_rate,
    "Number of Readmissions" as number_of_readmissions,
    "Start Date" as start_date,
    "End Date" as end_date
from {{ source('healthcare_raw', 'RAW_READMISSIONS') }}