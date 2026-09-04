import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def explain_anomaly(anomaly: dict) -> str:
    prompt = f"""You are a senior data engineer reviewing automated data quality alerts.
    
An anomaly was detected in a Brazilian e-commerce dataset (Olist). Here are the details:

- Table: {anomaly['table']}
- Column: {anomaly['column']}
- Check type: {anomaly['check_type']}
- Severity: {anomaly['severity']}
- Value: {anomaly['value']}
- Raw message: {anomaly['message']}

Write a clear, concise explanation (3-4 sentences) that:
1. Describes what the anomaly is in plain English
2. Gives a likely real-world reason WHY this might be happening
3. States which downstream processes might be affected
4. Suggests one concrete next step

Write as if you're a senior data engineer sending a Slack message to your team.
Do NOT use bullet points. Write in flowing prose."""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return response.text


def explain_all_anomalies(report: list) -> list:
    explained_report = []
    for anomaly in report:
        explanation = explain_anomaly(anomaly)
        enriched = {**anomaly, "llm_explanation": explanation}
        explained_report.append(enriched)
    return explained_report