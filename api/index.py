# api/index.py
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Initialize the FastAPI app
app = FastAPI()

# --- CORRECTED CORS CONFIGURATION ---
# This middleware adds the necessary CORS headers to every response.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # This sets Access-Control-Allow-Origin: *
    allow_credentials=True,
    allow_methods=["*"],      # This sets Access-Control-Allow-Methods
    allow_headers=["*"],      # This sets Access-Control-Allow-Headers
)

# --- Load the data ---
# This part is correct.
try:
    df = pd.read_json("api/q-vercel-latency.json")
except FileNotFoundError:
    df = pd.DataFrame()

# --- Define the API endpoint ---
# This part is correct.
@app.post("/")
async def get_analytics(request: Request):
    """
    Accepts a POST request with regions and a threshold,
    and returns calculated metrics.
    """
    if df.empty:
        return {"error": "Telemetry data not found on server."}

    body = await request.json()
    regions_to_process = body.get("regions", [])
    threshold = body.get("threshold_ms", 0)
    
    results = {}

    for region in regions_to_process:
        region_df = df[df['region'] == region]
        
        if not region_df.empty:
            avg_latency = region_df['latency_ms'].mean()
            p95_latency = region_df['latency_ms'].quantile(0.95)
            avg_uptime = region_df['uptime_pct'].mean()
            breaches = len(region_df[region_df['latency_ms'] > threshold])
            
            results[region] = {
                "avg_latency": avg_latency,
                "p95_latency": p95_latency,
                "avg_uptime": avg_uptime,
                "breaches": breaches
            }

    return results