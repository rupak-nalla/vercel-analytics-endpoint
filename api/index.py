# api/index.py
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Initialize the FastAPI app
app = FastAPI()

# --- Enable CORS ---
# This allows POST requests from any website (as required by the prompt)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["POST"], # Allows only POST requests
    allow_headers=["*"],
)

# --- Load the data ---
# CHANGE: Load data from JSON instead of CSV.
# This is done once when the serverless function starts, making it efficient.
try:
    # Use read_json for the telemetry.json file
    df = pd.read_json("api/q-vercel-latency.json")
except FileNotFoundError:
    # If the file is not found, create an empty DataFrame to avoid crashing
    df = pd.DataFrame()

# --- Define the API endpoint ---
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
        # Filter the DataFrame for the current region
        region_df = df[df['region'] == region]
        
        if not region_df.empty:
            # Calculate all the required metrics
            avg_latency = region_df['latency_ms'].mean()
            p95_latency = region_df['latency_ms'].quantile(0.95)
            avg_uptime = region_df['uptime_pct'].mean()
            breaches = len(region_df[region_df['latency_ms'] > threshold])
            
            # Store the results
            results[region] = {
                "avg_latency": avg_latency,
                "p95_latency": p95_latency,
                "avg_uptime": avg_uptime,
                "breaches": breaches
            }

    return results