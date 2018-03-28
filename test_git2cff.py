import pytest

from github_cff_extractor import GitHubCffGuesser


@pytest.mark.parametrize("input, output_first, output_last", [
    ('Dave McKain', 'Dave', 'McKain'),
    ('Dave.McKain', 'Dave', 'McKain'),
    ('Ronaldo', '', 'Ronaldo'),
    ('Neil Chue Hong', 'Neil Chue', 'Hong'),  # FIXME: Bad!!!
])
def test_parse_human_name(input, output_first, output_last):
    first, last = GitHubCffGuesser(None)._parse_human_name(input)
    assert output_first == first
    assert output_last == last
