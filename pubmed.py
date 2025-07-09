"""
Module for fetching and filtering PubMed research papers.
"""
from typing import List, Dict, Optional
import requests
import xml.etree.ElementTree as ET

PUBMED_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

class PubMedPaper:
    def __init__(self, pubmed_id: str, title: str, pub_date: str, non_academic_authors: List[str], company_affiliations: List[str], corresponding_email: Optional[str]):
        self.pubmed_id = pubmed_id
        self.title = title
        self.pub_date = pub_date
        self.non_academic_authors = non_academic_authors
        self.company_affiliations = company_affiliations
        self.corresponding_email = corresponding_email

    def to_dict(self) -> Dict[str, str]:
        return {
            "PubmedID": self.pubmed_id,
            "Title": self.title,
            "Publication Date": self.pub_date,
            "Non-academic Author(s)": ", ".join(self.non_academic_authors),
            "Company Affiliation(s)": ", ".join(self.company_affiliations),
            "Corresponding Author Email": self.corresponding_email or ""
        }

def fetch_pubmed_ids(query: str, retmax: int = 100) -> List[str]:
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": retmax,
        "retmode": "xml"
    }
    resp = requests.get(PUBMED_ESEARCH_URL, params=params)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)
    return [id_elem.text for id_elem in root.findall(".//Id")]

def fetch_pubmed_details(pubmed_ids: List[str]) -> List[PubMedPaper]:
    if not pubmed_ids:
        return []
    params = {
        "db": "pubmed",
        "id": ",".join(pubmed_ids),
        "retmode": "xml"
    }
    resp = requests.get(PUBMED_EFETCH_URL, params=params)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)
    papers = []
    for article in root.findall(".//PubmedArticle"):
        pubmed_id = article.findtext(".//PMID") or ""
        title = article.findtext(".//ArticleTitle") or ""
        pub_date = article.findtext(".//PubDate/Year") or ""
        authors = article.findall(".//Author")
        non_academic_authors = []
        company_affiliations = []
        corresponding_email = None
        for author in authors:
            affiliation = author.findtext("AffiliationInfo/Affiliation") or ""
            name = " ".join(filter(None, [author.findtext("ForeName"), author.findtext("LastName")]))
            if is_non_academic(affiliation):
                non_academic_authors.append(name)
                company = extract_company(affiliation)
                if company:
                    company_affiliations.append(company)
            email = extract_email(affiliation)
            if email and not corresponding_email:
                corresponding_email = email
        papers.append(PubMedPaper(pubmed_id, title, pub_date, non_academic_authors, company_affiliations, corresponding_email))
    return papers

def is_non_academic(affiliation: str) -> bool:
    academic_keywords = ["university", "college", "institute", "school", "hospital", "center", "centre", "faculty", "department", "academy", "clinic", "laboratory", "lab"]
    return not any(word in affiliation.lower() for word in academic_keywords)

def extract_company(affiliation: str) -> Optional[str]:
    # Heuristic: return the first comma-separated segment not matching academic keywords
    academic_keywords = ["university", "college", "institute", "school", "hospital", "center", "centre", "faculty", "department", "academy", "clinic", "laboratory", "lab"]
    location_keywords = ["usa", "uk", "germany", "france", "canada", "india", "china", "japan", "australia", "boston", "new york", "london", "paris", "berlin", "delhi", "tokyo", "sydney", "ma", "ny", "ca", "tx", "il", "wa", "on", "qc"]
    segments = [seg.strip() for seg in affiliation.split(',')]
    for seg in segments:
        seg_lower = seg.lower()
        if not seg:
            continue
        if any(word in seg_lower for word in academic_keywords):
            continue
        if any(word in seg_lower for word in location_keywords):
            continue
        # skip if segment is just a state/country abbreviation
        if len(seg) <= 3 and seg.isupper():
            continue
        return seg
    return None

def extract_email(affiliation: str) -> Optional[str]:
    import re
    match = re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', affiliation)
    return match.group(0) if match else None
