from typing import Tuple

from yaqti.helpers import split_version
from yaqti.helpers import is_valid_url

import pytest
from pytest import mark


@mark.parametrize('input,expected', (
    ('5.9.0', (5, 9, 0)),
    ('5.11.0', (5, 11, 0)),
    ('5.9.5', (5, 9, 5)),
    ('5.12.11', (5, 12, 11)),
    ('6.0.0', (6, 0, 0)),
    ('6.1.2', (6, 1, 2)),
))
def test_split_version(input: str, expected: Tuple[int, int, int]) -> None:
    output = split_version(input)
    assert expected == output


@mark.parametrize('input', ('5.9.a', '5.110', '~.9.a', '6.-1,2'))
def test_split_version_bad(input: str) -> None:
    with pytest.raises(ValueError):
        split_version(input)


@mark.parametrize('url,result', (('http://www.google.com', True), ('http://www.facebook.com', True),
                                 ('http://google.co.uk', True), ('http://www.bad-url.datkj', False)))
def test_is_valid_url(url: str, result: bool):
    assert is_valid_url(url) == result


@mark.parametrize('url', ('www.google.com', 'facebook.com', 'google.co.uk', 'www.bad-url.datkj'))
def test_is_valid_url_missing_http(url: str):
    assert is_valid_url(url) == False
