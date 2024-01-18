import os

import requests

from typing import Dict, Optional

from requests.auth import HTTPBasicAuth
from pprint import pprint

MOCHI_API_BASE_URL = 'https://app.mochi.cards/api/'

# The mochi API returns a default of 10 items per request, which isn't very many.
# We  increase this to 100, which is the maximum supported by the API.
DEFAULT_LIMIT = 100

GET = 'GET'
POST = 'POST'


def _make_api_request(url, method=GET, req_data=None):
    """
    Make a request to the Mochi API. Will raise an exception if the request fails.

    Note that the MOCHI_API_KEY environment variable must be set in order for this to work.
    """
    res = requests.request(method, url, data=req_data, auth=HTTPBasicAuth(os.environ.get('MOCHI_API_KEY'), ''))

    if res.status_code != 200:
        raise Exception(f'API request failed with status code {res.status_code}: {res.text}')

    return res.json()


def list_decks():
    url = MOCHI_API_BASE_URL + 'decks'
    data = _make_api_request(url)

    return data['docs']


def _matches_optional_filters(deck, filters: Dict[str, str]) -> bool:
    for key, value in filters.items():
        if deck[key] != value:
            return False
    return True


def get_deck_id_by_name(deck_name: str, parent_id=None) -> Optional[str]:
    """
    Given a deck name, return the deck ID. Deck name is case-insensitive.

    Note that a deck's name is not guaranteed to be unique. If you want to ensure that you find the correct deck, you
    can optionally specify a parent deck ID.
    """
    filters = {}
    if parent_id:
        filters['parent-id'] = parent_id

    for deck in list_decks():
        if deck['name'].lower() == deck_name.lower() and _matches_optional_filters(deck, filters):
            return deck['id']

    return None


def list_cards_in_deck(deck_id: str):
    url = MOCHI_API_BASE_URL + 'cards/?deck-id=' + deck_id
    data = _make_api_request(url)

    return data


def _format_content_for_card(front: str, back: str):
    return f'{front}\n---\n{back}'


def create_card_in_deck(deck_id: str, front: str, back: str):
    req_data = {
        'deck-id': deck_id,
        'content': _format_content_for_card(front, back),
        # 'review-reverse?': True  # There seems to be a bug in the Mochi API where this doesn't work. :(
    }

    url = MOCHI_API_BASE_URL + 'cards'
    data = _make_api_request(url, method=POST, req_data=req_data)

    return data


if __name__ == '__main__':
    deck_name = 'Vocabulary'  # Should have parent deck-id gI87UIK5; deck-id vhi7b9gq.

    deck_id = get_deck_id_by_name(deck_name, parent_id='gI87UIK5')
    print(f'Found deck id: {deck_id}')

    if not deck_id:
        print('Could not find deck with name: ' + deck_name)
        exit(1)

    # cards = list_cards_in_deck(deck_id)
    # pprint(cards)

    data = create_card_in_deck(deck_id, 'hello', 'óla')
    pprint(data)
