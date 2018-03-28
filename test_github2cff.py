import pytest

from github_cff_extractor import GitHubCffGuesser


@pytest.mark.parametrize("input, output_first, output_last", [
    ('Dave McKain', 'Dave', 'McKain'),
    ('Dave.McKain', 'Dave', 'McKain'),
    ('Ronaldo', '', 'Ronaldo'),
    ('Neil Chue Hong', 'Neil Chue', 'Hong'),  # FIXME: Bad!!!
])
def test_parse_human_name(input, output_first, output_last):
    g = GitHubCffGuesser(None)
    first, last = g._parse_human_name(input)
    assert output_first == first
    assert output_last == last


def test_to_cff_date():
    g = GitHubCffGuesser(None)
    output = g.to_cff_date('2018-03-28 15:00:00')
    assert output == '2018-03-28'
