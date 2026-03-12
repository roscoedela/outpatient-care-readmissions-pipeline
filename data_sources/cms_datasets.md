# Data Sources

## Medicare Physician & Other Practitioners

Source:
https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners

Purpose:
Measure outpatient physician utilization and spending information on use, payments, and submitted charges organized by National Provider Identifier (NPI), Healthcare Common Procedure Coding System (HCPCS) code, and place of service)

Key Fields:
- npi
- hcpcs_code
- number_of_services
- average_medicare_payment
- state

Role In Project:
This is the primary dataset for measuring outpatient care volume, service mix, and cost at the state level.

## Hospital Readmissions Reduction Program

Source:
https://data.cms.gov/provider-data/dataset/9n3s-kdb3

Purpose:
Measure hospital readmission outcomes for certain ailments (heart attack (AMI), heart failure (HF), pneumonia, chronic obstructive pulmonary disease (COPD), hip/knee replacement (THA/TKA), and coronary artery bypass graft surgery (CABG) by the expected rate of readmissions)

Key Fields:
- facility_id
- measure_name
- readmission_ratio
- state

Role in project:
This dataset provides the primary outcome metric for evaluating whether higher outpatient utilization and spending are associated with lower hospital readmission rates.

## HCAHPS Patient Survey

Source:
https://data.cms.gov/provider-data/dataset/dgck-syfz

Purpose:
A list of hospital ratings for the Hospital Consumer Assessment of Healthcare Providers and Systems (HCAHPS). HCAHPS is a national, standardized survey of hospital patients about their experiences during a recent inpatient hospital stay.

Key Fields:
- facility_id
- survey_measure
- score
- state

Role in project:
This dataset is used to incorporate patient experience into the analysis and to examine whether patient satisfaction is associated with hospital readmission outcomes.
