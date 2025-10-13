This is a [Next.js](https://nextjs.org/) project bootstrapped with [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).

## Setup

You will need the `OPENAI_API_KEY` environment variable.
```bash
export OPENAI_API_KEY="your_openai_api_key"
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


## Implementation Details
### Overview
The application integrates advertisements into the toy OpenEvidence frontend. The underlying logic through which these ads are generated/included in the site is the following:

The query is parsed by an LLM in order to extract disease keywords. These keywords are then validated against the purchased categories for the different drug companies. The category that was purchased for the greatest amount of money then has the ad for that category shown. The images for the ads themselves were generating using Google Gemini AI image generation.

The ads, when clicked take the user to a link for the drug relevant to the disease category and company that had purchased that disease category.

The ads and their information are stored in the categories_ads.json file.

### Data Collection
Several different kinds of data are collected in the app. The number of times each disease is mentioned as a keyword is recorded and stored in the disease_counts.json file. Additionally, the number of times each ad is clicked on is recorded in the ad_clicks.json file. Also, the total amount of time spent on each query is stored in disease_times.json (organized by disease). The number of mentions of uncategorized diseases is available in uncategorized.json.


### Additonal Pages of the App
There are some additional URLs that you can visit that provide some additional information and some of the data that has been collected.

From the perspective of advertisers (drug companies), there is the desire to purchase another disease category. To this end, you can visit http://localhost:3000/categories_for_sale
This link shows the most mentioned disease that aren't yet purchased. This kind of view could then be used to sell disease categories to drug companies as a revenue source.

Also, drug companies are likely to be interested in how much users are interacting with their purchased drug categories. For this purpose, you can visit http://localhost:3000/company/pfizer or http://localhost:3000/company/genentech or http://localhost:3000/company/gsk or http://localhost:3000/company/eli%20lilly to see the numbers of clicks, mentions, and amount of time spent for each disease for each company.
