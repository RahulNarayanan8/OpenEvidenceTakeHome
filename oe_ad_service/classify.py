import os
import openai
import json
client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
DATA_PATH = "disease_counts.json"
UNCATEGORIZED = "uncategorized.json"
ADS_PATH = "ad_clicks.json"
TIME_PATH = "disease_times.json"


def load_time_data():
    if os.path.exists(TIME_PATH):
        with open(TIME_PATH, "r") as f:
            return json.load(f)
    return {}

def save_time_data(data):
    with open(TIME_PATH, "w") as f:
        json.dump(data, f, indent=2)

def log_query_time(diseases, duration_ms):
    """
    diseases: list of strings
    company: string
    duration_ms: integer
    """
    data = load_time_data()

    for disease in diseases:
        if disease not in data:
            data[disease] = 0
        data[disease] += duration_ms

    save_time_data(data)



def get_highest_paying_ad(query):
    keywords = identify_keywords(query)
    
    with open('categories_ads.json', 'r') as f:
        data = json.load(f)
    
    matched_ads = []

    for keyword in keywords:
        if keyword.lower() in data:
            ad_info = data[keyword.lower()]
            matched_ads.append({
                "category": keyword,
                "ad_path": ad_info["ad_path"],
                "company": ad_info["company"],
                "cost": ad_info["category_cost"],
                "link": ad_info["link"]
            })
    
    # If no matching ads, return None
    if not matched_ads:
        return None

    # Select the ad with the highest cost
    best_ad = max(matched_ads, key=lambda x: x["cost"])
    return best_ad
    


def load_counts():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    return {}

def save_counts(counts):
    with open(DATA_PATH, "w") as f:
        json.dump(counts, f, indent=2)

def load_unclaimed():
    if os.path.exists(UNCATEGORIZED):
        with open(UNCATEGORIZED, "r") as f:
            return json.load(f)
    return {}

def save_unclaimed(unclaimed):
    with open(UNCATEGORIZED, "w") as f:
        json.dump(unclaimed, f, indent=2)


def load_ads():
    if os.path.exists(ADS_PATH):
        with open(ADS_PATH, "r") as f:
            return json.load(f)
    return {}


def identify_keywords(query):
    response = gpt_lookup(query)
    if "NO DISEASES" in response:
        return []
    lines = response.split("\n")
    lines = [" ".join(line.split(" ")[1:]) for line in lines]

    counts = load_counts()
    for disease in lines:
        counts[disease.lower()] = counts.get(disease.lower(), 0) + 1
    save_counts(counts)


    uncategorized = load_unclaimed()
    ads = load_ads()
    for disease in lines:
        if disease.lower() not in ads:
            uncategorized[disease.lower()] = uncategorized.get(disease.lower(), 0) + 1
    save_unclaimed(uncategorized)


    return lines


def gpt_lookup(query):
    prompt = prepare_prompt(query)
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1000,
    )
    gpt_response = response.choices[0].message.content

    return gpt_response


def prepare_prompt(user_question):
    return f"""You are tasked with identifying the relevant diseases or conditions that mentioned, referenced, or relevant to the user question
    being asked below. You will return the output in the following manner:
    
    Example Output

    1. Arthritis
    2. Colon Cancer
    3. Back Pain
    
    
    There may be any number of diseases or even no diseases. In the case where there are no diseases or conditions to return, output the following:
    
    Example Output
    
    NO DISEASES


    Return nothing else but the content in the format of the example outputs above.
    
    
    Here is the user question:
    {user_question}
    """
