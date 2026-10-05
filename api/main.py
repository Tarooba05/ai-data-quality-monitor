import sys
import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

load_dotenv()

# make sure imports work regardless of how the app is launched
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from checks.quality_checks import run_all_checks
from llm.explainer import explain_all_anomalies

app = FastAPI(
    title="AI Data Quality Monitor",
    description="Automated data quality checks with LLM-generated explanations",
    version="1.0.0"
)

# in-memory store for the latest report
latest_report = None
last_run_time = None

# load data once at startup so we're not re-reading CSVs on every request
BASE_PATH = r'C:\Users\taroo\OneDrive\Desktop\Project\data-quality-monitor\data\Brazillion Ecommerce'

@app.on_event("startup")
def load_data():
    global orders, order_items, customers
    orders = pd.read_csv(BASE_PATH + r'\olist_orders_dataset.csv')
    order_items = pd.read_csv(BASE_PATH + r'\olist_order_items_dataset.csv')
    customers = pd.read_csv(BASE_PATH + r'\olist_customers_dataset.csv')
    print("Data loaded successfully")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "last_run": last_run_time,
        "message": "AI Data Quality Monitor is running"
    }


@app.post("/run-check")
def run_check():
    global latest_report, last_run_time
    
    try:
        # run anomaly detection
        raw_report = run_all_checks(orders, order_items, customers)
        
        # add LLM explanations
        explained_report = explain_all_anomalies(raw_report)
        
        # store for /latest-report
        latest_report = explained_report
        last_run_time = datetime.now().isoformat()
        
        return {
            "status": "success",
            "run_time": last_run_time,
            "anomalies_found": len(explained_report),
            "report": explained_report
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/latest-report")
def get_latest_report():
    if latest_report is None:
        raise HTTPException(
            status_code=404,
            detail="No report available yet. Call POST /run-check first."
        )
    
    return {
        "status": "success",
        "run_time": last_run_time,
        "anomalies_found": len(latest_report),
        "report": latest_report
    }