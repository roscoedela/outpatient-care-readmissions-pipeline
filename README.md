# Outpatient Care Readmissions Pipeline

An end-to-end analytics engineering project that ingests, validates, transforms, and analyzes outpatient care, patient experience, and readmissions-related data, with a final Tableau dashboard used to surface state-level patterns in predicted readmission rates, risk burden, cost pressure, and patient satisfaction.

## Overview

This project began as a healthcare data pipeline and evolved into a full analytics engineering capstone. My goal was to move beyond simple reporting by building a workflow that could ingest and validate source data, transform it into analysis-ready structures, and support business facing insights through Tableau.

The final output is a state-level dashboard exploring how predicted readmission rates relate to patient survey ratings, average risk score, and cost per patient. In addition to building the technical workflow, I used this project to work through data modeling decisions, metric interpretation, and the challenge of turning pipeline outputs into a coherent analytical story. This is also a chance for me to use all of these tools at once as I have been limited in certain environments due to security reasons.

## Business Problem

Healthcare stakeholders need trustworthy, analysis ready data to understand patterns tied to patient outcomes and care experience. I personally started this wondering "Where are the places in America that people are happy within their provider system?".In this project, I explored how readmissions related metrics, patient satisfaction, and cost/risk indicators could be combined to answer questions such as:

- Which states show the highest predicted readmission rates?
- Is higher patient risk associated with higher readmission rates?
- Is lower patient satisfaction associated with worse readmission outcomes?
- How might cost pressure affect patient experience and operational performance?

This project was designed to show both the technical pipeline required to support analysis and the business-facing dashboard used to communicate results.

## Final Dashboard

The final Tableau dashboard, **State Level Readmissions and Patient Experience Dashboard**, presents:

- A U.S. map highlighting where predicted readmission rates are highest
- A Top 10 states ranking by average predicted readmission rate
- A scatterplot comparing average risk score vs. predicted readmission rate
- A scatterplot comparing average patient survey star rating vs. predicted readmission rate
- Additional context using cost per patient and narrative interpretation to explain state level variation and outliers

## Key Questions Answered

This dashboard and pipeline were built to explore the following questions:

- Where are predicted readmission rates highest?
- Do higher-risk states also show higher readmission rates?
- Are lower patient satisfaction scores associated with worse readmission performance?
- Which states appear to be outliers, and what operational or demographic factors might help explain them?

## Project Evolution

This project changed substantially as I worked through it.

### Phase 1: Pipeline Build
I initially focused on getting the technical pipeline running end to end, including ingestion, validation, and orchestration.
<img width="796" height="273" alt="Screenshot 2026-03-16 at 1 28 48 PM" src="https://github.com/user-attachments/assets/15d953af-8362-4aee-a102-01fc8e1fbf4a" />
<img width="797" height="285" alt="readmissions_unique_states_numeric_summary" src="https://github.com/user-attachments/assets/afeda597-0975-4deb-bac3-f57beda3dba4" />


### Phase 2: Debugging and Reliability
As the project developed, I ran into validation and execution issues that forced me to rethink pieces of the implementation. This stage made the project stronger by pushing me to focus on reliability, not just first-pass execution. 

First, creating the tests and schema yaml was paramount. After a few failures, seeing that certain columns and models couldn't be tested the same helped these pass 
<img width="1171" height="582" alt="Screenshot 2026-03-29 at 12 00 37 PM" src="https://github.com/user-attachments/assets/0a0eee9f-6934-4234-978a-8b4cc6a70815" />

<img width="764" height="489" alt="Screenshot 2026-03-17 at 9 15 47 AM" src="https://github.com/user-attachments/assets/b001e0c4-4708-41cf-adc2-55578bd6d26f" />
<img width="796" height="553" alt="Screenshot 2026-03-17 at 9 15 30 AM" src="https://github.com/user-attachments/assets/f752057d-09bb-42bf-9b25-d0a09f262daf" />
<img width="1378" height="781" alt="Screenshot 2026-03-17 at 8 23 57 PM" src="https://github.com/user-attachments/assets/45c992ca-a117-443f-ae5f-4e92b36bdb6c" />
<img width="1166" height="625" alt="Screenshot 2026-03-17 at 7 18 16 PM" src="https://github.com/user-attachments/assets/f1d57222-78b6-4c5c-bf71-38c8a9f983a5" />

<img width="819" height="666" alt="airflow_dag_green" src="https://github.com/user-attachments/assets/106e4a8b-e0ee-41aa-b55b-c9efc0417639" />



### Phase 3: Data Understanding and Modeling
Once the pipeline was more stable, my attention shifted to the data itself: table grain, join logic, metric definitions, and how sources such as readmissions, patient experience, and provider-related data should be connected and communicated. <img width="999" height="598" alt="Screenshot 2026-03-23 at 12 29 20 PM" src="https://github.com/user-attachments/assets/bcb7c9af-2b39-48ae-bf50-2bb029314bdf" />


### Phase 4: Analytics Framing
The project then evolved from technical infrastructure into analytical storytelling. I began testing relationships between patient satisfaction, cost, ailments, risk score, and predicted readmission burden to identify useful patterns and possible business interpretations/solutions.
<img width="1014" height="246" alt="Screenshot 2026-03-20 at 9 40 21 PM" src="https://github.com/user-attachments/assets/6316bacf-6274-49a4-9eb8-434d3d380cc5" />

### Phase 5: Dashboard and Communication
Finally, I translated the analysis into Tableau so the pipeline outputs could be consumed visually and interpreted more easily by a stakeholder audience.

<img width="1293" height="1080" alt="Screenshot 2026-03-22 at 3 20 55 PM" src="https://github.com/user-attachments/assets/95962a17-08e4-40c6-8ae3-993c9bd77948" />
Interactive Dashboard:

https://public.tableau.com/app/profile/rooscol.rozambert/viz/HealthcareReadmissionsDashboard_17741121167600/Dashboard1

## Tech Stack

- Python
- SQL
- Airflow
- Docker
- Tableau
- GitHub

## Data Sources

This project combines multiple healthcare-related datasets to support readmissions analysis and patient experience exploration.

### Readmissions Data
Used as the central outcome oriented dataset for comparing predicted readmission rates across states.
https://data.cms.gov/provider-data/dataset/9n3s-kdb3

### Patient Experience / Survey Data
Used to bring in average patient survey star ratings and better understand how patient experience relates to readmissions. 
https://data.cms.gov/provider-data/dataset/dgck-syfz

### Risk and Cost Metrics
Used to compare average risk burden and cost per patient across states.

### Provider / Healthcare Context Data
Used to support broader modeling, joins, and interpretation throughout the project workflow.
https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider-and-service/data

## Pipeline and Transformation Workflow

The project follows a staged analytics engineering workflow:

- Ingest raw healthcare data into Snowflake
- Validate source quality and build Airflow orchestration
- Run dbt staging and marts to create analysis-ready tables
- Debug transformation and testing issues until the workflow ran reliably
- Clarify table grain, joins, and metric definitions
- Build a state-level summary model for downstream analysis
- Test relationships between readmission, risk, satisfaction, services, and cost
- Translate the findings into a Tableau dashboard

A major part of the project involved moving from raw technical execution into clearer metric definitions and business ready outputs and thinking downstream as I am planning on expanding this with more quality of life measures. 

## Tableau Dashboard Design

Link to dashboard: https://public.tableau.com/app/profile/rooscol.rozambert/viz/HealthcareReadmissionsDashboard_17741121167600/Dashboard1

The Tableau dashboard was designed around a few core analytical views:

### Geographic Overview
A state-level map helps identify where predicted readmission rates are concentrated geographically.

### Ranked Comparison
A Top 10 bar chart highlights the highest-readmission states for fast comparison.

### Risk vs. Readmission
A scatterplot shows the positive relationship between average risk score and average predicted readmission rate.

### Satisfaction vs. Readmission
A second scatterplot shows the inverse relationship between patient satisfaction and predicted readmission rate.

### Narrative Interpretation
A written text block summarizes patterns, likely drivers, and meaningful outliers such as New Jersey, Utah, Alaska, or other states depending on the cut and interpretation.

## Key Findings

This project produced several directional findings:

- States with higher average risk scores generally showed higher predicted readmission rates
- Lower patient satisfaction tended to align with higher predicted readmission burden
- Cost pressure appeared relevant to patient experience, though it was not always the strongest explanatory factor
- Some states behaved like outliers, suggesting that local health culture, demographics, care coordination, or system complexity may matter alongside cost and risk burden

These findings are exploratory and meant to support discussion, not claim definitive causality.

## Challenges and Iterations

Some of the most important challenges in this project included:

- Debugging source validation and pipeline execution issues
- Rethinking parts of the workflow when the initial structure was not sufficient
- Clarifying the grain and meaning of each dataset before joining
- Interpreting healthcare metrics carefully enough to avoid misleading comparisons
- Translating a technically complex workflow into a clean dashboard and story

This was one of the most valuable parts of the project because it pushed me to think like both a data engineer and an analytics engineer. This also was a large set of data so it made me have to think of memory and effieciency more than other projects and tasks at work. 

## Lessons Learned
Raw tables should usually stay close to the source, and if the column names, formats, or structure are awkward, the staging layer is the right place to standardize them.

I learned that relying on awkward raw column names makes downstream SQL and dbt models harder to maintain. When raw column references become brittle, renaming and standardizing them in staging is often the cleanest long-term solution.
I learned that getting the SQL to run is not enough. Before comparing metrics, I had to understand the grain of each table and whether the measures were actually comparable at the level of analysis I wanted. A successful pipeline run does not automatically mean the analysis is correct. I had to distinguish between technical completion and analytical validity.

## How to Run the Project
### 1. Clone the repository

```bash
git clone https://github.com/roscoedela/outpatient-care-readmissions-pipeline.git
cd outpatient-care-readmissions-pipeline
```
### 2. Set up a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```
### 3. Install dependencies

```bash
pip install -r requirements.txt
```

##Make sure you have all of the technical requirements:

Python
Docker
Airflow
dbt
Snowflake access
Tableau Desktop or Tableau Public for the dashboard layer

## Virtual Environment
python -m venv .venv
source .venv/bin/activate

## Install Dependencies
pip install -r requirements.txt

### 4. Confirm required tools and access

Before running the project, make sure you have:

- Python
- Docker
- Airflow
- dbt
- Snowflake access
- Tableau Public or Tableau Desktop

## Repository Structure

```bash
outpatient-care-readmissions-pipeline/
├── dags/
├── ingestion/
├── transformations/
├── docs/
│   └── screenshots/
├── tableau/
├── notebooks/
├── data/
├── tests/
└── README.md
