import requests
import pandas as pd
import time
import random
import os

# CONFIGURATION
BASE_URL = "https://candidates.myfuturejobs.gov.my/api/jobs?facets=CONTRACT_TYPE==2,CONTRACT_TYPE==3,CONTRACT_TYPE==4,CONTRACT_TYPE==5,CONTRACT_TYPE==6,CONTRACT_TYPE==7,EDUCATION==5,RECENCY==2WEEKSAGO,STATE==Selangor"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://candidates.myfuturejobs.gov.my/search-jobs/description?RECENCY=2WEEKSAGO&STATE=Selangor&EDUCATION=5&selected=a8797c3bae634c89a5e69967d0ff42fb&CONTRACT_TYPE=2,3,4,5,6,7"
}

#Change this keyword to search for different types of jobs
SEARCH_KEYWORD = "Selangor"
#Each page returns 30 jobs
RESULTS_PER_PAGE = 30
#How many pages to fetch
MAX_PAGES = 20  

# SCRAPER FUNCTION
def scrape_myfuturejobs(keyword=SEARCH_KEYWORD, max_pages=MAX_PAGES):
    all_jobs = []

    print(f"Searching for jobs with state: '{keyword}' ...\n")

    for page in range(max_pages):
        offset = page * RESULTS_PER_PAGE
        params = {
            "offset": offset,
            "limit": RESULTS_PER_PAGE,
            "keywords": keyword
        }

        try:
            response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
        except Exception as e:
            print(f"Error connecting: {e}")
            break

        # Check HTTP response
        if response.status_code != 200:
            print(f"Page {page+1}: Failed with status {response.status_code}")
            break

        data = response.json()
        results = data.get("results") or data.get("data") or []

        if not results:
            print(f"No more results found at page {page+1}. Stopping.")
            break

        for job in results:
            job_id = job.get("id", "")
            title = job.get("positionTitle", "")
            company = job.get("companyName", "")
            location = job.get("location", "")
            salary = job.get("actualWages", "")
            contract_type = job.get("contractType", "")

            all_jobs.append({
                "job_id": job_id,
                "title": title,
                "company": company,
                "location": location,
                "salary": salary,
                "contractType": contract_type,
                "source": "MyFutureJobs"
            })

        print(f"Page {page+1}: Retrieved {len(results)} jobs ({len(all_jobs)} total)")
        time.sleep(2 + random.random() * 2)  #polite delay between requests

    #Convert to DataFrame
    df_new = pd.DataFrame(all_jobs)
    file_path = "jobs_myfuturejobs.csv"

    if not df_new.empty:
        if os.path.exists(file_path):
            df_old = pd.read_csv(file_path, encoding="utf-8-sig")
            df_combined = pd.concat([df_old, df_new], ignore_index=True)
            df_combined.drop_duplicates(subset=["job_id"], inplace=True)
            df_combined.to_csv(file_path, index=False, encoding="utf-8-sig")
            print(f"\nMerged and saved total {len(df_combined)} unique jobs to '{file_path}'")
        else:
            df_new.to_csv(file_path, index=False, encoding="utf-8-sig")
            print(f"\nSaved {len(df_new)} jobs to new file '{file_path}'")
    else:
        print("No new jobs were retrieved.")

    return df_new

if __name__ == "__main__":
    df = scrape_myfuturejobs(keyword=SEARCH_KEYWORD, max_pages=MAX_PAGES)
    print("\nSample results:")
    print(df.head())