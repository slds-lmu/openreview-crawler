"""OpenReview client to query the API."""

from typing import Final

import openreview
from openreview.api import Note

STATUS: Final[list] = ['all', 'accepted', 'withdrawn', 'desk-rejected']


class ORClient:
    """Base client."""

    def __init__(self, username: str, password: str) -> None:
        """Instantiate client."""
        self.client = openreview.Client(
            baseurl='https://api2.openreview.net',
            username=username,
            password=password,
        )

    def print_venues(self) -> None:
        """Print names of listed venues."""
        print(self.client.get_group(id='venues').members)

    def get_papers(self, venue_id: str, status: str = 'all') -> list[Note]:
        """Get all submitted papers."""
        if status not in STATUS:
            raise ValueError(
                f'`status` must be one of {", ".join([x for x in STATUS])}'
            )
        query_id = self._get_query_id(venue_id, status)
        if status == 'all':
            papers = self.client.get_all_notes(invitation=f'{venue_id}/-/{query_id}')
        else:
            papers = self.client.get_all_notes(content={'venueid': query_id})
        return list(papers)

    def _get_query_id(self, venue_id: str, status: str) -> str:
        """Get submission name."""
        venue_group = self.client.get_group(venue_id)
        if status == 'all':
            query_str = 'submission_name'
        elif status == 'accepted':
            return venue_id
        elif status == 'withdrawn':
            query_str = 'withdrawn_venue_id'
        elif status == 'desk-rejected':
            query_str = 'desk_rejected_venue_id'
        else:
            raise ValueError()
        return venue_group.content[query_str]['value']
