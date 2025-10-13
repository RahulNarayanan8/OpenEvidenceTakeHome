from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from classify import get_highest_paying_ad, log_query_time
from datetime import datetime, timezone
import json
import os
from pydantic import BaseModel
from typing import List

app = FastAPI()

from fastapi.staticfiles import StaticFiles

app.mount("/ad_images", StaticFiles(directory="ad_images"), name="ad_images")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get_ad")
def get_ad(query: str = Query(...)):
    ad = get_highest_paying_ad(query)
    if ad is None:
        return {"ad": None}
    return {"ad": ad}


CLICK_DATA_PATH = "ad_clicks.json"

def load_clicks():
    if os.path.exists(CLICK_DATA_PATH):
        with open(CLICK_DATA_PATH, "r") as f:
            return json.load(f)
    return []

def save_clicks(clicks):
    with open(CLICK_DATA_PATH, "w") as f:
        json.dump(clicks, f, indent=2)

@app.post("/track_click")
async def track_click(request: Request):
    """
    Tracks an ad click event.
    Expected JSON payload:
    {
        "disease": "diabetes",
        "company": "eli lilly"
    }
    """
    time = str(datetime.now(timezone.utc))
    data = await request.json()

    disease = data.get("disease").lower()

    clicks = load_clicks()
    clicks[disease]["clicks"] +=1
    save_clicks(clicks)

    return {"status": "ok", "logged": time}

@app.get("/categories_for_sale")
def categories_for_sale():
    path = "uncategorized.json"

    if not os.path.exists(path):
        return {"unclaimed_diseases": []}

    with open(path, "r") as f:
        data = json.load(f)

    # Handle both possible structures gracefully
    sorted_diseases = sorted(
        data.items(),
        key=lambda x: x[1]["mentions"] if isinstance(x[1], dict) else x[1],
        reverse=True
    )

    # Normalize to consistent output
    formatted = []
    for d, v in sorted_diseases:
        mentions = v["mentions"] if isinstance(v, dict) else v
        formatted.append({"disease": d, "mentions": mentions})

    return {"unclaimed_diseases": formatted}



def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}


@app.get("/company_summary/{company_name}")
def company_summary(company_name: str):
    mentions = load_json("disease_counts.json")
    clicks = load_json("ad_clicks.json")
    categories = load_json("categories_ads.json")
    times = load_json("disease_times.json")

    # Get the purchased categories for this company
    purchased_categories = [cat for cat, info in categories.items() if info["company"].lower() == company_name.lower()]

    summary = []
    for cat in purchased_categories:
        summary.append({
            "disease": cat,
            "mentions": mentions.get(cat, 0),
            "clicks": clicks.get(cat, {}).get("clicks", 0),
            "times": times.get(cat,0)
        })

    return {"company": company_name, "summary": summary}




class TimeLogRequest(BaseModel):
    diseases: List[str]
    duration_ms: int

@app.post("/log_query_time")
def log_time_endpoint(data: TimeLogRequest):
    log_query_time(data.diseases, data.duration_ms)
    return {"status": "ok"}