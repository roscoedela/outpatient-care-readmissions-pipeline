with physicians_by_state as (

    select
        state_code,
        sum(try_to_double(total_beneficiaries::varchar)) as total_outpatient_beneficiaries,
        sum(try_to_double(total_services::varchar)) as total_outpatient_services,
        avg(try_to_double(total_medicare_payment_amount::varchar)) as avg_outpatient_payment,
        avg(try_to_double(beneficiary_avg_risk_score::varchar)) as avg_beneficiary_risk_score
    from {{ ref('stg_physicians') }}
    where state_code is not null
    group by state_code

),

readmissions_by_state as (

    select
        state_code,
        avg(try_to_double(excess_readmission_ratio::varchar)) as avg_excess_readmission_ratio,
        avg(try_to_double(predicted_readmission_rate::varchar)) as avg_predicted_readmission_rate,
        avg(try_to_double(expected_readmission_rate::varchar)) as avg_expected_readmission_rate,
        sum(try_to_double(number_of_discharges::varchar)) as total_discharges
    from {{ ref('stg_readmissions') }}
    where state_code is not null
    group by state_code

),

hcahps_by_state as (

    select
        state_code,
        avg(try_to_double(hcahps_linear_mean_value::varchar)) as avg_patient_experience_score,
        avg(try_to_double(survey_response_rate_percent::varchar)) as avg_survey_response_rate,
        sum(try_to_double(number_of_completed_surveys::varchar)) as total_completed_surveys
    from {{ ref('stg_hcahps') }}
    where state_code is not null
    group by state_code

)

select
    coalesce(p.state_code, r.state_code, h.state_code) as state_code,
    p.total_outpatient_beneficiaries,
    p.total_outpatient_services,
    p.avg_outpatient_payment,
    p.avg_beneficiary_risk_score,
    r.avg_excess_readmission_ratio,
    r.avg_predicted_readmission_rate,
    r.avg_expected_readmission_rate,
    r.total_discharges,
    h.avg_patient_experience_score,
    h.avg_survey_response_rate,
    h.total_completed_surveys
from physicians_by_state p
full outer join readmissions_by_state r
    on p.state_code = r.state_code
full outer join hcahps_by_state h
    on coalesce(p.state_code, r.state_code) = h.state_code