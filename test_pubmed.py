import pytest
from paperslist import pubmed

def test_is_non_academic():
    assert pubmed.is_non_academic("Pfizer Inc., New York, NY, USA")
    assert not pubmed.is_non_academic("Harvard University, Boston, MA, USA")

def test_extract_company():
    assert pubmed.extract_company("Pfizer Inc., New York, NY, USA") == "Pfizer Inc."
    assert pubmed.extract_company("Harvard University, Boston, MA, USA") is None

def test_extract_email():
    aff = "Pfizer Inc., New York, NY, USA. john.doe@pfizer.com"
    assert pubmed.extract_email(aff) == "john.doe@pfizer.com"
    aff2 = "No email here"
    assert pubmed.extract_email(aff2) is None
