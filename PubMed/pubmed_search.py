# search script for PubMed

import requests
import xml.etree.ElementTree as ET
import csv

# Base URLs for the NCBI Entrez API
BASE_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
BASE_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# Define search query, copied from Appendix
query = """
(("LLM"[Title/Abstract] OR "Large Language Model"[Title/Abstract] OR "ChatGPT"[Title/Abstract]) 
AND ("Psychotherapy"[Title/Abstract] OR "Psychological Counseling"[Title/Abstract] OR 
"Psychotherapeutic Intervention"[Title/Abstract] OR "Cognitive Behavioral Therapy"[Title/Abstract] 
OR "Motivational Interviewing"[Title/Abstract] OR "Dialectical Behavioral Therapy"[Title/Abstract] 
OR "Psychodynamic Therapy"[Title/Abstract] OR "Interpersonal Therapy"[Title/Abstract] 
OR "Exposure Therapy"[Title/Abstract]))
"""

# search parameters
search_params = {
    "db": "pubmed",
    "term": query,
    "retmax": 5000,  # an upperbound in case something goes wrong. shouldn't reach this number.
    "retmode": "xml"
}

# Perform search
search_response = requests.get(BASE_SEARCH_URL, params=search_params)
search_response.raise_for_status()
search_root = ET.fromstring(search_response.text)

# Extract PubMed IDs from the search results
pmids = [id_elem.text for id_elem in search_root.findall(".//Id")]

if not pmids:
    print("No articles found.")
    exit()

# Fetch details for the retrieved PMIDs
fetch_params = {
    "db": "pubmed",
    "id": ",".join(pmids),
    "retmode": "xml"
}
fetch_response = requests.get(BASE_FETCH_URL, params=fetch_params)
fetch_response.raise_for_status()
fetch_root = ET.fromstring(fetch_response.text)

# Extract relevant info
results = []
for article in fetch_root.findall(".//PubmedArticle"):
    title_elem = article.find(".//ArticleTitle")
    title = title_elem.text if title_elem is not None else "No title"
    
    journal_elem = article.find(".//Title")
    journal = journal_elem.text if journal_elem is not None else "No journal"
    
    year_elem = article.find(".//PubDate/Year")
    year = year_elem.text if year_elem is not None else "No year"
    
    author_list = article.findall(".//Author")
    authors = []
    for author in author_list:
        last_name = author.find("LastName")
        first_name = author.find("ForeName")
        if last_name is not None and first_name is not None:
            authors.append(f"{first_name.text} {last_name.text}")
    authors_str = ", ".join(authors) if authors else "No authors"
    
    results.append([title, authors_str, journal, year])



# Save results to a CSV file in the current python file location
with open("pubmed_results.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "Authors", "Journal", "Year"])
    writer.writerows(results)

print("Results saved to pubmed_results.csv") # end of execution
