# api/index.py
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Initialize the FastAPI app
app = FastAPI()

# --- THIS IS THE CORRECT CORS CONFIGURATION ---
# It adds the required headers to every response from your API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # This sends the "Access-Control-Allow-Origin: *" header.
    allow_credentials=True,
    allow_methods=["*"],      # Allows all methods, including the browser's "preflight" OPTIONS request.
    allow_headers=["*"],      # Allows all headers, like "Content-Type".
)

# --- Load the data ---
# This code loads the JSON file from the same directory.
try:
    df = pd.read_json("api\\q-vercel-latency.json")
except Exception:
    df = pd.DataFrame() # Create an empty DataFrame if loading fails, to prevent a crash.

# --- Define the API endpoint ---
@app.post("/")
async def get_analytics(request: Request):
    try:
        df = pd.read_json("api/q-vercel-latency.json")
    except Exception:
        df = pd.DataFrame() # Create an empty DataFrame if loading fails, to prevent a crash.

    if df.empty:
        return {"error": "Telemetry data not found on server. Check file path and content."}

    try:
        body = await request.json()
        regions_to_process = body.get("regions", [])
        threshold = body.get("threshold_ms", 0)
    except Exception:
        return {"error": "Invalid JSON body received."}
    
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