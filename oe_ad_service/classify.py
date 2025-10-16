import os
import openai
import json
client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
DATA_PATH = "disease_counts.json"
UNCATEGORIZED = "uncategorized.json"
ADS_PATH = "ad_clicks.json"
TIME_PATH = "disease_times.json"
TOTAL_QUERIES_PATH = "total_queries.json"
QUERY_COST_PATH = "query_costs.json"

# Loading and Saving Time Spent on Query Data
def load_time_data():
    if os.path.exists(TIME_PATH):
        with open(TIME_PATH, "r") as f:
            return json.load(f)
    return {}

def save_time_data(data):
    with open(TIME_PATH, "w") as f:
        json.dump(data, f, indent=2)

# Loading, Saving, and Incremeneting Total Number of Queries Data
def load_total_data():
    if os.path.exists(TOTAL_QUERIES_PATH):
        with open(TOTAL_QUERIES_PATH, "r") as f:
            return json.load(f)
    return {}
def save_total_data(data):
    with open(TOTAL_QUERIES_PATH, "w") as f:
        json.dump({"total_queries": data}, f)

def increment_total_queries():
    total = load_total_data().get("total_queries", 0)
    total+=1
    save_total_data(total)

# Logging time spent on queries in json
def log_query_time(diseases, duration_ms):
    data = load_time_data()

    for disease in diseases:
        if disease not in data:
            data[disease] = 0
        data[disease] += duration_ms

    save_time_data(data)

    increment_total_queries()


def get_highest_paying_ad(query):
    """
    This function gets the highest paying ad given a query. It identifies the keyword (if any) whose disease category was purchased
    for the greatest amount of money and returns the relevant information for that ad

    Args:
        query (str): the user question
    
    Returns:
        dict: the relevant information for ad
    """
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
    

# Loading and saving counts of disease mentions
def load_counts():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    return {}

def save_counts(counts):
    with open(DATA_PATH, "w") as f:
        json.dump(counts, f, indent=2)

# Loading and saving unpurchased disease categories mentions
def load_unclaimed():
    if os.path.exists(UNCATEGORIZED):
        with open(UNCATEGORIZED, "r") as f:
            return json.load(f)
    return {}

def save_unclaimed(unclaimed):
    with open(UNCATEGORIZED, "w") as f:
        json.dump(unclaimed, f, indent=2)

# Loading clicks data
def load_ads():
    if os.path.exists(ADS_PATH):
        with open(ADS_PATH, "r") as f:
            return json.load(f)
    return {}


def identify_keywords(query):
    """
    This function extracts the disease keywords from the GPT response. It then returns list of diseases. 
    It also updates some of the information about disease mentions in the json files

    Args:
        query (str): the user question

    Returns:
        list[str]: the disease(s) mentioned in the prompt
    """
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

# Loading and saving cost data for the LLM queries
def load_query_cost():
    if os.path.exists(QUERY_COST_PATH):
        with open(QUERY_COST_PATH, "r") as f:
            return json.load(f)
    return {}

def save_query_cost(data):
    with open(QUERY_COST_PATH, "w") as f:
        json.dump(data, f, indent=2)

def gpt_lookup(query):
    """
    This function calls GPT to identify the keywords in a prompt. It also computes the cost of the query to identify the keywords and
    updates the query cost json information.

    Args:
        query (str): The user query
    
    Returns:
        (str): The GPT response containing the diseases mentioned in the prompt
    """
    prompt = prepare_prompt(query)
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1000,
    )
    usage = response.usage
    prompt_tokens = usage.prompt_tokens
    completion_tokens = usage.completion_tokens

    input_cost = 0.005 / 1000
    output_cost = 0.015 / 1000

    total_cost = prompt_tokens * input_cost + completion_tokens * output_cost

    cost_dict = load_query_cost()
    cost_dict["query"] = cost_dict.get("query", 0) + total_cost

    save_query_cost(cost_dict)
    gpt_response = response.choices[0].message.content

    return gpt_response


def prepare_prompt(user_question):
    """
    This function prepares the prompt that will be used to identify the keywords in the user question with a formatted string.

    Args:
        user_question (str): the User question

    Returns:
        (str): the prompt that GPT will use to identify the keywords that are being mentioned in the user question.
    """
    return f"""You are tasked with identifying the relevant diseases or conditions that mentioned, referenced, or relevant to the user question
    being asked below. You will return the output in the following manner:
    
    Example Output

    1. Arthritis
    2. Colon Cancer
    3. Allergy
    
    
    There may be any number of diseases or even no diseases. In the case where there are no diseases or conditions to return, output the following:
    
    Example Output
    
    NO DISEASES


    Return nothing else but the content in the format of the example outputs above.
    
    
    Here is the user question:
    {user_question}
    """
