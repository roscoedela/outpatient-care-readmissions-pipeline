"""
ingest.py — Healthcare Copilot Embedding Pipeline
Reads CSVs, converts rows into rich text documents, embeds via OpenAI,
stores in FAISS local index. Run once before launching the Streamlit app.
"""

import os
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

load_dotenv()

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_DIR = os.path.join(DATA_DIR, "faiss_index")

STATE_NAMES = {
    "AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California",
    "CO":"Colorado","CT":"Connecticut","DE":"Delaware","FL":"Florida","GA":"Georgia",
    "HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa",
    "KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland",
    "MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi",
    "MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada","NH":"New Hampshire",
    "NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina",
    "ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania",
    "RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota","TN":"Tennessee",
    "TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington",
    "WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming","DC":"Washington D.C.",
    "PR":"Puerto Rico","GU":"Guam","VI":"Virgin Islands",
}

def safe_float(val, decimals=2):
    try:
        return round(float(val), decimals)
    except (TypeError, ValueError):
        return None

def fmt(val, decimals=2, suffix=""):
    v = safe_float(val, decimals)
    return f"{v}{suffix}" if v is not None else "N/A"

def build_physician_docs(df):
    docs = []
    for _, row in df.iterrows():
        code = str(row["STATE_CODE"]).strip()
        name = STATE_NAMES.get(code, code)
        text = (
            f"State: {name} ({code})\n"
            f"Disease Burden — Cancer: {fmt(row.get('CANCER_PCT'),1,'%')}, "
            f"Diabetes: {fmt(row.get('DIABETES_PCT'),1,'%')}, "
            f"Stroke: {fmt(row.get('STROKE_PCT'),1,'%')}, "
            f"Parkinson's: {fmt(row.get('PARKINSONS_PCT'),1,'%')}, "
            f"Depression: {fmt(row.get('DEPRESSION_PCT'),1,'%')}\n"
            f"Average Beneficiary Risk Score: {fmt(row.get('AVG_RISK_SCORE'),3)} (higher = sicker population)\n"
            f"Cost per Patient (Medicare): {fmt(row.get('COST_PER_PATIENT'),2,' USD')}\n"
            f"Patient Out-of-Pocket Cost per Patient: {fmt(row.get('PATIENT_COST_PER_PATIENT'),2,' USD')}\n"
            f"Medicare Coverage Ratio: {fmt(row.get('MEDICARE_COVERAGE_RATIO'),3)}\n"
            f"Services per Patient: {fmt(row.get('SERVICES_PER_PATIENT'),2)}"
        )
        docs.append(Document(page_content=text,
            metadata={"source": "physician_state_metrics", "state_code": code, "state_name": name}))
    return docs

def build_analysis_docs(df):
    docs = []
    for _, row in df.iterrows():
        code = str(row["STATE_CODE"]).strip()
        name = STATE_NAMES.get(code, code)
        text = (
            f"State: {name} ({code})\n"
            f"Outpatient Volume: {fmt(row.get('TOTAL_OUTPATIENT_BENEFICIARIES'),0)} total beneficiaries\n"
            f"Average Outpatient Payment: {fmt(row.get('AVG_OUTPATIENT_PAYMENT'),2,' USD')}\n"
            f"Average Beneficiary Risk Score: {fmt(row.get('AVG_BENEFICIARY_RISK_SCORE'),3)}\n"
            f"Readmissions — Predicted Rate: {fmt(row.get('AVG_PREDICTED_READMISSION_RATE'),2,'%')}, "
            f"Expected Rate: {fmt(row.get('AVG_EXPECTED_READMISSION_RATE'),2,'%')}, "
            f"Excess Readmission Ratio: {fmt(row.get('AVG_EXCESS_READMISSION_RATIO'),4)} (>1.0 = worse than expected)\n"
            f"Patient Satisfaction — Star Rating: {fmt(row.get('AVG_PATIENT_SURVEY_STAR_RATING'),2)}/5, "
            f"HCAHPS Linear Mean: {fmt(row.get('AVG_HCAHPS_LINEAR_MEAN_VALUE'),2)}, "
            f"Survey Response Rate: {fmt(row.get('AVG_SURVEY_RESPONSE_RATE_PERCENT'),1,'%')}, "
            f"Total Completed Surveys: {fmt(row.get('TOTAL_COMPLETED_SURVEYS'),0)}"
        )
        docs.append(Document(page_content=text,
            metadata={"source": "state_healthcare_analysis", "state_code": code, "state_name": name}))
    return docs

def build_correlation_docs(df):
    lines = []
    for _, row in df.iterrows():
        rel  = str(row["RELATIONSHIP"]).strip()
        corr = safe_float(row["CORRELATION"])
        if corr is None:
            continue
        strength = (
            "strong positive" if corr >= 0.7 else
            "moderate positive" if corr >= 0.4 else
            "weak positive" if corr > 0 else
            "strong negative" if corr <= -0.7 else
            "moderate negative" if corr <= -0.4 else
            "weak negative"
        )
        lines.append(f"- {rel}: correlation = {corr:.4f} ({strength})")
    text = (
        "Pre-computed Statistical Correlations across all states:\n"
        + "\n".join(lines)
        + "\n\nInterpretation: Values near +1.0 = strong positive; near -1.0 = strong inverse."
    )
    return [Document(page_content=text,
        metadata={"source": "correlation_findings", "state_code": "ALL", "state_name": "All States"})]

def main():
    print("Loading CSVs...")
    physician_df = pd.read_csv(os.path.join(DATA_DIR, "physician_state_metrics.csv"))
    analysis_df  = pd.read_csv(os.path.join(DATA_DIR, "state_healthcare_analysis.csv"))
    corr_df      = pd.read_csv(os.path.join(DATA_DIR, "correlation_findings.csv"))

    valid_codes  = set(STATE_NAMES.keys())
    physician_df = physician_df[physician_df["STATE_CODE"].isin(valid_codes)]
    analysis_df  = analysis_df[analysis_df["STATE_CODE"].isin(valid_codes)]

    print(f"  Physician metrics: {len(physician_df)} states")
    print(f"  Healthcare analysis: {len(analysis_df)} states")
    print(f"  Correlation findings: {len(corr_df)} relationships")

    print("\nBuilding documents...")
    docs  = build_physician_docs(physician_df)
    docs += build_analysis_docs(analysis_df)
    docs += build_correlation_docs(corr_df)
    print(f"  Total documents: {len(docs)}")

    print("\nEmbedding and storing in FAISS...")
    embeddings  = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(FAISS_DIR)
    print(f"  Saved FAISS index to {FAISS_DIR}")
    print("\n✅ Ingestion complete. Run: streamlit run app.py")

if __name__ == "__main__":
    main()
