"""Utility functions."""
import re

import click
import pandas as pd
from nltk.stem.snowball import SnowballStemmer
from openreview.api import Note


def extract_papers(papers: list[Note]) -> pd.DataFrame:
    """Export info from papers as csv."""
    rows = []
    for p in papers:
        nr = p.number
        title = p.content['title']['value']
        authors = ', '.join(p.content['authors']['value'])
        abstract = p.content['abstract']['value']
        url = f'https://openreview.net/pdf?id={p.id}'
        rows.append([nr, title, authors, abstract, url])
    colnames = ['id', 'title', 'authors', 'abstract', 'url']
    return pd.DataFrame(rows, columns=colnames)


def get_credentials() -> tuple:
    """Prompt user for credentials via CLI."""
    usr = click.prompt('Enter OpenReview username', hide_input=False)
    pw = click.prompt('Enter OpenReview password', hide_input=True)
    return usr, pw


def flag_keyword(text: str, keyword: str) -> int:
    """Flag presence of keyword in text (fuzzy search)."""
    keyword = keyword.lower()
    text = text.lower()
    keyword_clean = _clean_and_stem_text(keyword)
    text_clean = _clean_and_stem_text(text)
    if ' and ' in keyword_clean:
        keyword_list = re.split(' and ', keyword_clean)
        is_match = all([k in text_clean for k in keyword_list])
    elif ' or ' in keyword_clean:
        keyword_list = re.split(' or ', keyword_clean)
        is_match = any([k in text_clean for k in keyword_list])
    else:
        is_match = keyword_clean in text_clean
    return int(is_match)


def _clean_and_stem_text(text: str) -> str:
    """Clean text and return stemmed tokens."""
    stemmer = SnowballStemmer('english')
    text = re.sub('-', ' ', text.lower())
    text = re.sub(r'[^\w\s]', '', text)
    text_stemmed = [stemmer.stem(x) for x in re.split(' ', text)]
    return ' '.join(x for x in text_stemmed)
