This is a [Next.js](https://nextjs.org/) project bootstrapped with [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).

## Demo
You can find a demo video [here](https://www.youtube.com/watch?v=-zZ3ri2Xnk4)

## Setup

You will need the `OPENAI_API_KEY` environment variable.
```bash
export OPENAI_API_KEY="your_openai_api_key"
```
Create and activate environment with:
```bash
python3 -m venv env
source env/bin/activate
```
Install dependencies with
```bash
pip install -r oe_ad_service/requirements.txt
```

## Run

To run the application please follow the instructions below:

First cd into the oe_ad_service directory:
```bash
cd oe_ad_service/
```
Then start the backend server with the following command
```bash
uvicorn app:app --reload
```

In a separate terminal, cd into oe-toy-frontend directory:
```bash
cd oe-toy-frontend/
```

Run the development server:

```bash
OPENAI_API_KEY=KEY npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

Backend and frontend servers should be running simultaneously for full functionality.

## Implementation Details
### Overview
The application integrates advertisements into the toy OpenEvidence frontend. The underlying logic through which these ads are generated/included in the site is the following:

The query is parsed by an LLM in order to extract disease keywords. These keywords are then validated against the purchased categories for the different drug companies. The category that was purchased for the greatest amount of money then has the ad for that category shown. The images for the ads themselves were generating using Google Gemini AI image generation (there are some typos in the ads because of this).

The ads, when clicked take the user to a link for the drug relevant to the disease category and company that had purchased that disease category. Each disease category is owned by one drug company. The drug company pays a certain price to acquire a category and the price is related to how common the disease is (Obesity is more expensive and more common than HIV). The costs represent a monthly payment for the category.

The ads and their information are stored in the categories_ads.json file.

Unit tests for functionality (specifically in the classify.py file) are available in tests.py

### Data Collection
Several different kinds of data are collected in the app. The number of times each disease is mentioned as a keyword is recorded and stored in the disease_counts.json file. Additionally, the number of times each ad is clicked on is recorded in the ad_clicks.json file. Also, the total amount of time spent on each query is stored in disease_times.json (organized by disease). The number of mentions of uncategorized diseases is available in uncategorized.json. The costs of LLM queries are tracked in query_costs.json. The total number of queries is logged in total_queries.json. Lastly, the mentions of unpurchased diseases categories are found in uncategorized.json


### Additonal Pages of the App
There are some additional URLs that you can visit that provide some additional information and some of the data that has been collected.

From the perspective of advertisers (drug companies), there is the desire to see what other diseases are being mentioned by users. To this end, you can visit [http://localhost:3000/categories_for_sale](http://localhost:3000/categories_for_sale)
This link shows the most mentioned disease that aren't yet purchased. This kind of view could then be used to sell disease categories to drug companies as a revenue source.

Also, drug companies are likely to be interested in how much users are interacting with their purchased drug categories. For this purpose, you can visit [http://localhost:3000/company/pfizer](http://localhost:3000/company/pfizer) or [http://localhost:3000/company/genentech](http://localhost:3000/company/genentech) or [http://localhost:3000/company/gsk](http://localhost:3000/company/gsk) or [http://localhost:3000/company/eli%20lilly](http://localhost:3000/company/eli%20lilly) to see the numbers of clicks, mentions, and amount of time spent for each disease for each company.

Another page in the app is the revenue tracker which you can visit at [http://localhost:3000/revenue](http://localhost:3000/revenue). This page computes and displays revenue metrics for OpenEvidence. It tracks the amounts that different drug companies are paying for advertising as well as the costs incurred by calling LLMs as part of the main question and answer app (as well as the LLM calls to identify what diseases are being asked about). Additionally, the page shows profit metrics and the different revenue shares for the different drug companies.

The final page in the app provides functionality for bidding. A category that was purchased by one company can be bought by another company for a higher price. This adds some market-like functionality to the app which is a better reflection of real-world advertising. Currently, only diseases that have already been purchased can be bid on - those that are unpurchased cannot be bid on.Once a company, buys a disease category, that company's ad will be shown in the app (and will link that company's drug). This page of the app can be found by visiting [http://localhost:3000/buy_category](http://localhost:3000/buy_category).

(There are buttons to all these pages in the app)

## Future Directions
Below are some additional features or directions I could have pursued given additional time.

### More Robust Storage: 
Currently data is stored in json files which is not very scalable or secure. In the long term, it would be better to use some kind of database or cloud storage.

### Nearby Pharmacies: 
In order to provide a more seamless user experience, nearby pharmacies could be shown below the advertisement, so that users could check on the availability of the drug being advertised. 

### More Complex Category Ownership: 
Currently, categories are owned by a single company at any given time. Providing support for multiple companies owning a given drug category would be a better reflection of real advertising. If this were the case, the selection criterion for which ad is ultimately displayed would also become more sophisticated, likely involving randomness weighted by how much each company is paying for that category.

### Embedding Studies:
Studies about the drugs being advertised could be found using LLMs or other tools and linked in the app alongside their associated ad.

### Personalized Ad Recommendations:
If this app is being used by real doctors, then it could integrate information about the clinics they work at, the previous patients they've seen, their specialization, their location, etc. to display more targeted advertisements (if OpenEvidence is willing to collect such data). 
