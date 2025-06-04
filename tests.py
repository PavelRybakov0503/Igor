import pytest
from unittest.mock import MagicMock, patch
from parser import GoldAppleParser


@pytest.fixture
def gold_apple_parser():
    return GoldAppleParser(products_url="mock_products_url",
                           product_card_url="mock_product_card_url",
                           city_id="mock_city_id",
                           headers={})


@pytest.fixture
def mock_response():
    return MagicMock()


@pytest.fixture
def mock_post():
    with patch('requests.post') as mock:
        yield mock


def test_get_products(gold_apple_parser, mock_response, mock_post):
    mock_response.json.return_value = {'data': {'products': [{'itemId': '1', 'url': '/product1', 'name': 'Product 1', 'price': {'actual': {'amount': '10'}}, 'reviews': {'rating': '5'}}]}}
    mock_post.return_value = mock_response

    result = gold_apple_parser.get_products()

    assert isinstance(result, dict)
    assert len(result['data']['products']) == 1
    assert result['data']['products'][0]['itemId'] == '1'


def test_get_product_card(gold_apple_parser, mock_response, mock_post):
    mock_response.json.return_value = {'data': {
        'productDescription': [{'text': 'Описание', 'content': 'Product description'},
                               {'text': 'Применение', 'content': 'Usage instructions'},
                               {'text': 'Дополнительная информация', 'content': 'Made in Italy'}]}}
    mock_post.return_value = mock_response

    result = gold_apple_parser.get_product_card('1')

    assert isinstance(result, MagicMock)
    assert result.json() == {'data': {
        'productDescription': [{'text': 'Описание', 'content': 'Product description'},
                               {'text': 'Применение', 'content': 'Usage instructions'},
                               {'text': 'Дополнительная информация', 'content': 'Made in Italy'}]}}


def test_parse_products(gold_apple_parser):
    response_data = {'data': {'products': [{'itemId': '1', 'url': '/product1', 'name': 'Product 1', 'price': {'actual': {'amount': '10'}}, 'reviews': {'rating': '5'}}]}}
    result = gold_apple_parser.parse_products(response_data)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0][0] == '1'


def test_parse_country_with_country_info(gold_apple_parser):
    text = "<br>Italy<br>"
    result = gold_apple_parser.parse_country(text)
    assert result == 'Italy'


def test_parse_product_card_without_country_info(gold_apple_parser):
    response_data = {'data': {'productDescription': [{'text': 'Описание', 'content': 'Product description'},
                                                     {'text': 'Применение', 'content': 'Usage instructions'},
                                                     {'text': 'Дополнительная информация',
                                                      'content': 'No country information'}]}}
    result = gold_apple_parser.parse_product_card(MagicMock(return_value=response_data))

    assert isinstance(result, tuple)
    assert len(result) == 3
    assert result[2] == ''
