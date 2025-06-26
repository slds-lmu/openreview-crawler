# openreview_crawler

Mini package to crawl submissions from OpenReview

## Install

Set up virtual environment of your choice.

Install via GitHub (e.g., by putting `openreview-crawler @ git+https://github.com/slds-lmu/openreview-crawler` in your `requirements.txt` file).

## Example usage

💡 Easy way: copy notebook already using the crawler ➡️ e.g., [this one](https://github.com/slds-lmu/causalfairml-jc/blob/main/jc-13.ipynb)

```python
from openreview_crawler.client import ORClient
from openreview_crawler.utils import get_credentials, extract_papers, flag_keyword
import re
import os
import pandas as pd
```

Prompt for credentials and instantiate client

```python
usr, pw = get_credentials()
my_client = ORClient(usr, pw)
```

Find out conference ID for, say, ICML 2023

```python
print([x for x in my_client.get_venues() if 'ICML' in x and '2023' in x])
# ...
venue_id = 'ICML.cc/2023/Conference'
```

Get accepted papers and extract relevant info

```python
accepted = my_client.get_papers(venue_id, 'accepted')
papers = extract_papers(accepted)
```

Perform keyword search, adding a binary column for each keyword in a list.
Keywords can be
- compositions like *information theory* :arrow_right: flag with 1 if composition appears whole
- OR constructions like *NN or neural network* :arrow_right: flag with 1 if either appears
- AND constructions like *tuning and categorical* :arrow_right: flag if both appear

```python
keywords = ['information theory', 'NN or neural network', 'tuning and categorical']
for k in keywords:
    col = []
    for r in range(len(papers)):
        row = papers.iloc[r, :]
        is_match = max(flag_keyword(row['title'], k), flag_keyword(row['abstract'], k))
        col.append(is_match)
    papers[re.sub(' ', '_', k)] = col
```
