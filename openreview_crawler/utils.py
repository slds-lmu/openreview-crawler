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
    # OR combinations are handled first, incl. possible AND combinations within
    if ' or ' in keyword_clean:
        keyword_list = re.split(' or ', keyword_clean)
        matches = []
        for kw in keyword_list:
            if ' and ' in kw:
                kw_list = re.split(' and ', kw)
                is_match = _check_and_combinations(text_clean, kw_list)
            else:
                is_match = _check_single(text_clean, kw)
            matches.append(int(is_match))
        is_match_all = 1 if sum(matches) > 0 else 0
    # Next, handle AND combinations without OR
    elif ' and ' in keyword_clean:
        keyword_list = re.split(' and ', keyword_clean)
        is_match_all = int(_check_and_combinations(keyword_clean, keyword_list))
    # Last, handle single-type keywords
    else:
        is_match_all = int(_check_single(text_clean, keyword_clean))
    return is_match_all


def _clean_and_stem_text(text: str) -> str:
    """Clean text and return stemmed tokens."""
    stemmer = SnowballStemmer('english')
    text = re.sub('-', ' ', text.lower())
    text = re.sub(r'[^\w\s]', '', text)
    text_stemmed = [stemmer.stem(x) for x in re.split(' ', text)]
    return ' '.join(x for x in text_stemmed)


def _remove_whitespaces(text: str) -> str:
    """Remove whitespaces from text."""
    return re.sub(' +', '', text)


def _check_and_combinations(text: str, keyword_list: list[str]) -> bool:
    return all([k in text or _remove_whitespaces(k) in text for k in keyword_list])


def _check_single(text: str, keyword: str) -> bool:
    return any([keyword in text or _remove_whitespaces(keyword) in text])
