with readmissions_by_hospital as (

    select
        facility_id::varchar as facility_id,
        max(facility_name) as facility_name,
        max(state_code) as state_code,
        avg(try_to_double(excess_readmission_ratio::varchar)) as avg_excess_readmission_ratio,
        avg(try_to_double(predicted_readmission_rate::varchar)) as avg_predicted_readmission_rate,
        avg(try_to_double(expected_readmission_rate::varchar)) as avg_expected_readmission_rate,
        sum(try_to_double(number_of_discharges::varchar)) as total_discharges,
        count(*) as readmissions_measure_count
    from {{ ref('stg_readmissions') }}
    where facility_id is not null
    group by facility_id::varchar

),

hcahps_by_hospital as (

    select
        facility_id::varchar as facility_id,
        max(facility_name) as facility_name,
        max(state_code) as state_code,
        max(city) as city,
        max(zip_code) as zip_code,
        max(county) as county,
        max(telephone_number) as telephone_number,
        avg(try_to_double(patient_survey_star_rating::varchar)) as avg_patient_survey_star_rating,
        avg(try_to_double(hcahps_answer_percent::varchar)) as avg_hcahps_answer_percent,
        avg(try_to_double(hcahps_linear_mean_value::varchar)) as avg_hcahps_linear_mean_value,
        avg(try_to_double(survey_response_rate_percent::varchar)) as avg_survey_response_rate_percent,
        sum(try_to_double(number_of_completed_surveys::varchar)) as total_completed_surveys,
        count(*) as hcahps_measure_count
    from {{ ref('stg_hcahps') }}
    where facility_id is not null
    group by facility_id::varchar

)

select
    coalesce(r.facility_id, h.facility_id) as facility_id,
    coalesce(r.facility_name, h.facility_name) as facility_name,
    coalesce(r.state_code, h.state_code) as state_code,
    h.city,
    h.zip_code,
    h.county,
    h.telephone_number,
    r.avg_excess_readmission_ratio,
    r.avg_predicted_readmission_rate,
    r.avg_expected_readmission_rate,
    r.total_discharges,
    r.readmissions_measure_count,
    h.avg_patient_survey_star_rating,
    h.avg_hcahps_answer_percent,
    h.avg_hcahps_linear_mean_value,
    h.avg_survey_response_rate_percent,
    h.total_completed_surveys,
    h.hcahps_measure_count
from readmissions_by_hospital r
full outer join hcahps_by_hospital h
    on r.facility_id = h.facility_id