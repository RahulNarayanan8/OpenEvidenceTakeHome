from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from classify import get_highest_paying_ad, log_query_time, load_total_data, load_query_cost, load_ads
from datetime import datetime, timezone
import json
import os
from pydantic import BaseModel
from typing import List
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fastapi.responses import StreamingResponse
import validators


CLICK_DATA_PATH = "ad_clicks.json"

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
    """
    This function creates the endpoint for getting the highest paying ad that will be used in the frontend.

    Args:
        query: user question
    Returns:
        dict: dictionary containing the ad
    """

    ad = get_highest_paying_ad(query)
    if ad is None:
        return {"ad": None}
    return {"ad": ad}


# Loading and saving the clicks data
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

    Args:
        request: fastAPI request containing information about the ad clicked on
    Returns: 
        dict: containing the status and time of click
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
    """
    Endpoint for getting the categories that have been searched for/about but are not purchased by any company

    Args:
        None
    Returns:
        dict: containing unpurchased diseases and their numbers of mentions
    """
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


@app.get("/categories_for_sale_chart")
def categories_for_sale_chart():
    """
    Returns a bar chart (PNG) of unpurchased but mentioned disease categories.
    """
    path = "uncategorized.json"

    if not os.path.exists(path):
        return {"error": "No uncategorized data found."}

    with open(path, "r") as f:
        data = json.load(f)

    # Handle both flat and nested structures
    sorted_diseases = sorted(
        data.items(),
        key=lambda x: x[1]["mentions"] if isinstance(x[1], dict) else x[1],
        reverse=True
    )

    diseases = [d for d, _ in sorted_diseases][:10]  # top 10 for clarity
    mentions = [
        v["mentions"] if isinstance(v, dict) else v
        for _, v in sorted_diseases[:10]
    ]

    # --- Create bar chart ---
    fig, ax = plt.subplots(figsize=(8, 5), dpi=200)
    ax.barh(diseases[::-1], mentions[::-1], color="#4C9AFF")
    ax.set_xlabel("Mentions")
    ax.set_ylabel("Disease")
    ax.set_title("Top Unpurchased but Mentioned Disease Categories")
    plt.tight_layout()

    # --- Save to buffer ---
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")




# Helper function to get json content
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}


@app.get("/company_summary/{company_name}")
def company_summary(company_name: str):
    """
    Endpoint for getting company specific information about the drug categories they have purchased and relevant metrics regarding
    advertising

    Args:
        company_name (str): name of the company whose metrics you're getting

    Returns:
        dict: company name and metrics
    """

    mentions = load_json("disease_counts.json")
    clicks = load_json("ad_clicks.json")
    categories = load_json("categories_ads.json")
    times = load_json("disease_times.json")

    total_queries = load_total_data().get("total_queries",0)

    cat_prices = {}
    for disease in categories:
        cat_prices[disease] = categories[disease]["category_cost"]

    
    start_date = datetime(2025, 10, 10)
    today = datetime.now()
    days_passed = (today - start_date).days
    revenue_fraction = days_passed / 30

    # Get the purchased categories for this company
    purchased_categories = [cat for cat, info in categories.items() if info["company"].lower() == company_name.lower()]

    summary = []
    for cat in purchased_categories:
        summary.append({
            "disease": cat,
            "mentions": mentions.get(cat, 0),
            "clicks": clicks.get(cat,{}).get("clicks",0),
            "mentions_per_query": str(round((mentions.get(cat, 0) / total_queries if total_queries > 0 else 0) * 100, 3)) + "%",
            "clicks_per_mention": clicks.get(cat, {}).get("clicks", 0) / mentions.get(cat,0) if mentions.get(cat,0) > 0 else 0,
            "times": (times.get(cat,0) / 1000) / mentions.get(cat, 0) if mentions.get(cat, 0) > 0 else 0,
            "monthly_category_cost": cat_prices.get(cat, 0),
            "total_paid": revenue_fraction * cat_prices.get(cat, 0),
            "clicks_per_dollar": clicks.get(cat,{}).get("clicks",0) / (revenue_fraction * cat_prices.get(cat, 0)),
            "mentions_per_day": mentions.get(cat, 0) / days_passed,
            "clicks_per_day": clicks.get(cat,{}).get("clicks",0) / days_passed
        })

    return {"company": company_name, "summary": summary}


@app.get("/pie/total_paid/{company}")
def pie_total_paid(company: str):
    """
    Endpoint to get a pie chart of how much a company has paid for each one of their purchased drug categories

    Args:
        company (str): name of the company
    Returns:
        fastapi StreamingResponse containing the matplotlib graph
    """
    with open('categories_ads.json', 'r') as f:
        data = json.load(f)

    # Filter categories owned by this company
    labels = [cat for cat in data if data[cat]["company"].lower() == company.lower()]
    values = [data[cat]["category_cost"] for cat in labels]

    if not labels:
        return {"error": f"No categories found for company {company}"}

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.set_title(f"Total Paid per Category ({company})")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@app.get("/pie/total_clicks/{company}")
def pie_total_clicks(company: str):
    """
    Endpoint to get a pie chart of how many clicks the ads are receiving for each one of the company's purchased drug categories

    Args:
        company (str): name of the company
    Returns:
        fastapi StreamingResponse containing the matplotlib graph
    """
    with open('categories_ads.json', 'r') as f:
        ads_data = json.load(f)

    clicks_data = load_ads()  # {disease: clicks}

    # Filter for this company's categories
    labels = []
    values = []
    for cat, info in ads_data.items():
        if info["company"].lower() == company.lower():
            labels.append(cat)
            values.append(clicks_data[cat]["clicks"])

    if not labels:
        return {"error": f"No clicks for company {company}"}

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.set_title(f"Total Clicks per Category ({company})")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

@app.get("/revenue")
def revenue_tracker():
    """
    Endpoint for tracking the revenue and revenue-related metrics for OpenEvidence

    Args:
        None
    Returns:
        (dict): containing the revenue metrics
    """
    total_costs_data = load_query_cost()
    total_costs = total_costs_data.get("query", 0)

    # 2️⃣ Load ad purchase data (monthly revenues)
    with open("categories_ads.json", "r") as f:
        ad_data = json.load(f)

    # October 10th refers to the day on which all the companies purchased the categories
    # Also the day I received the assessment
    start_date = datetime(2025, 10, 10)
    today = datetime.now()
    days_passed = (today - start_date).days
    revenue_fraction = days_passed / 30

    company_revenue = {}
    total_revenue = 0
    for disease, info in ad_data.items():
        company = info["company"]
        monthly_cost = info.get("category_cost", 0)
        prorated = monthly_cost * revenue_fraction
        company_revenue[company] = company_revenue.get(company, 0) + prorated
        total_revenue += prorated

    net_profit = total_revenue - total_costs

    return {
        "total_time_months": round(revenue_fraction, 3),
        "total_api_costs_usd": round(total_costs, 2),
        "total_prorated_ad_revenue_usd": round(total_revenue, 2),
        "net_profit_usd": round(net_profit, 2),
        "profit_per_day": round(net_profit / days_passed, 2),
        "revenue_breakdown_by_company": {
            company: round(value, 2) for company, value in company_revenue.items()
        }
    }


@app.get("/revenue_chart")
def revenue_chart():
    """
    Endpoint for getting a piechart of different companies contribution to OE's revenue

    Args:
        None

    Returns:
        fastapi StreamingResponse containing the matplotlib plot image
    """
    # Reuse the revenue data from the tracker
    revenue_data = revenue_tracker()
    company_data = revenue_data["revenue_breakdown_by_company"]

    if not company_data:
        return {"error": "No revenue data available"}

    # Create pie chart
    fig, ax = plt.subplots(figsize=(5, 5))
    labels = list(company_data.keys())
    labels = [label.upper() for label in labels]
    values = list(company_data.values())

    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.set_title("Revenue Share by Company")

    # Save as bytes and return
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi = 200)
    buf.seek(0)
    plt.close(fig)

    return StreamingResponse(buf, media_type="image/png")




class TimeLogRequest(BaseModel):
    diseases: List[str]
    duration_ms: int

@app.post("/log_query_time")
def log_time_endpoint(data: TimeLogRequest):
    """
    Logging the times that users are spending on a query about some set of diseases
    """
    log_query_time(data.diseases, data.duration_ms)
    return {"status": "ok"}



@app.post("/purchase_category")
def purchase_category(purchase: dict):
    """
    This function provides the logic for approving the purchase of a disease category by a drug company. It verifies that the sale is valid
    (price is above current price, buying company is valid and not current owner, etc.). It also updates the json files to reflect the new owner of the
    category and the new advertisement/link
    """
    disease = purchase.get("disease")
    new_company = purchase.get("company")
    bid_price = float(purchase.get("bid_price"))
    new_link = purchase.get("ad_link")

    new_company = new_company.lower()

    # Load category data
    with open("categories_ads.json", "r") as f:
        ads_data = json.load(f)

    if disease not in ads_data:
        return {"error": "Disease category not found"}

    current_cost = ads_data[disease]["category_cost"]
    if bid_price < current_cost:
        return {"error": f"Bid must be at least {current_cost}"}
    
    if ads_data[disease]["company"] == new_company:
        return {"error": ads_data[disease]["company"] + " has already purchased " + disease}
    conversion = {"pfizer":"pfizer", 
                  "genentech": "genentech", 
                  "glaxo-smith kline": "gsk", 
                  "glaxo smith kline": "gsk", 
                  "glaxosmith kline": "gsk", 
                  "gsk": "gsk",
                  "lilly": "lilly",
                  "eli lilly": "lilly",
                  "elililly": "lilly",
                  "eli-lilly": "lilly"
                  }
    if new_company.lower() not in conversion:
        return {"error": ads_data[disease]["company"] + " is not in set of valid drug companies."}
    def is_float(s):
        try:
            float(s)
            return True
        except ValueError:
            return False
    if not is_float(bid_price):
        return {"error": "Invalid bid price."}
    
    if validators.url(new_link) != True:
        return {"error": "Invalid link."}
    
    new_image = "ad_images/"+ conversion[new_company] + "_" + "_".join(disease.split(" ")) + ".png"
        

    # Update ownership
    ads_data[disease]["company"] = new_company
    ads_data[disease]["category_cost"] = bid_price
    ads_data[disease]["ad_path"] = new_image
    ads_data[disease]["link"] = new_link

    # Save updates
    with open("categories_ads.json", "w") as f:
        json.dump(ads_data, f, indent=2)

    # Optionally reset click data
    with open("ad_clicks.json", "r") as f:
        click_data = json.load(f)

    if disease in click_data:
        click_data[disease] = {"clicks": 0, "mentions": 0}

    with open("ad_clicks.json", "w") as f:
        json.dump(click_data, f, indent=2)

    return {"message": f"{new_company} successfully purchased {disease} for ${bid_price}"}

@app.get("/categories_ads")
def get_categories():
    """
    This function provides an endpoint for getting the information about different ads for the diseases

    Args:
        None

    Returns:
        dict containing ad information
    """
    with open("categories_ads.json", "r") as f:
        data = json.load(f)
    return data
