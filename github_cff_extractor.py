import re

from github import Github


class GitHubCffGuesser:
    """
    This class extracts (guesses?) CFF metadata from a Github repository
    object.
    """

    def __init__(self, repo):
        self.repo = repo
        self.parsed = None

    def run(self):
        """
        This method performs the data extraction, storing the results within
        this Object.

        There's no real need to call this explicitly as it will be called lazily
        via output methods.
        """
        result = dict()
        result['title'] = self.repo.name
        result['authors'] = self._extract_contributors()
        result['repository_code'] = self.repo.html_url

        # Extract license data. This seems only to exist in the underlying raw data
        repo_raw = self.repo.raw_data
        license_raw = repo_raw['license']
        if license_raw['spdx_id']:
            result['license'] = license_raw['spdx_id']
        if license_raw['url']:
            result['license-url'] = license_raw['url']

        self._extract_release_info(result)
        self.parsed = result

    def _extract_release_info(self, result):
        """
        This tries to extract data from the best possible release information.
        """
        releases = list(self.repo.get_releases())
        tags = list(self.repo.get_tags())
        if len(releases):
            # Take most recent release
            latest_release = releases[0]
            result['version'] = latest_release.tag_name
            result['date_released'] = self.to_cff_date(latest_release.created_at)
        elif len(tags):
            # Take most recent tag
            latest_tag = tags[0]
            result['version'] = latest_tag.name
            result['date_released'] = self.to_cff_date(latest_tag.commit.commit.author.date)
        else:
            # No tags yet, so we'll take the last commit on the default branch
            assert self.repo.default_branch  # TODO: Check this!
            branch = self.repo.get_branch(self.repo.default_branch)
            result['version'] = branch.commit.sha
            result['date_released'] = self.to_cff_date(branch.commit.commit.author.date)

    def _parse_human_name(self, name):
        """
        Attempts to parse a human name from GitHub, returning a 2-item tuple

        FIXME: This does not work for people like Neil Chue Hong...!
        """
        words = re.split(r'\s+', name)
        if len(words) == 1 and name.count('.') == 1:
            # Looks like a firstname.lastname person
            return name.split('.')
        else:
            return ' '.join(words[0:-1]), words[-1]

    def _extract_contributors(self):
        """
        Extracts contributor information from this repository
        """
        result = []
        for contributor in self.repo.get_contributors():
            name = contributor.name
            if contributor.type == 'User':
                # This is a real person
                first, last = self._parse_human_name(name)
                result.append({
                    'family_names': last,
                    'given_names': first,
                })
            else:
                # It's an organisation (I think...)
                result.append({
                    'name': name
                })
        return result

    def to_cff_date(self, datetime):
        """
        Transforms a GitHub YYYY-MM-DD HH:MM:SS into a CFF date string
        """
        return str(datetime)[0:10]

    def _ensure_run(self):
        if not self.parsed:
            self.run()

    def as_dict(self):
        """
        Returns a dictionary of extracted CFF metadata.

        Keys agree with the names in CFF, except that '-' characters have
        been converted to '_'.
        """
        self._ensure_run()
        return self.parsed

    def to_cff_string(self):
        """
        This returns a CFF string representation of the parsed data

        TODO: This is tedious and messy. Can't we use a YAML dump instead?
        """
        parsed = self.as_dict()
        return '''
cff-version: 1.0.3
message: If you use this software, please cite it as below.        
title: {title}
abstract: {abstract}
version: {version}
{authors_formatted}date-released: {date_released}
repository-code: {repository_code}'''.format(
            title=parsed['title'],
            abstract=self.repo.description,
            version=parsed['version'],
            authors_formatted=self._format_authors(),
            date_released=parsed['date_released'],
            repository_code=parsed['repository_code'],
        )
        # TODO: Need to include license stuff.
        return result

    def _format_authors(self):
        formatted_items = []
        for a in self.as_dict()['authors']:
            if 'name' in a:
                # It's an organisation
                formatted_items.append('  - name: {}\n'.format(
                    a['name']))
            else:
                # It's a person
                formatted_items.append(
                    '  - family-names: {}\n    given-names: {}\n'.format(
                        a['family_names'], a['given_names']))
        return 'authors:\n' + ''.join(formatted_items)


# Example code
if __name__ == '__main__':

    # NOTE: Put the GitHub auth token in the file below for now. Do NOT commit this file to git :-)
    auth_token_file = 'auth_token.txt'

    with open(auth_token_file, 'r') as f:
        auth_token = f.read().strip()

    # TODO: These would normally be user-selectable inputs
    input_username = 'codemeta'
    input_reponame = 'codemeta'

    # This has releases + a newer tag!
    # Here we'd expect to take the last release rather than the last branch
    #input_username = 'citation-file-format'
    #input_reponame = 'cff-converter-python'

    # This has no releases, but lots of tags
    #input_username = 'davemckain'
    #input_reponame = 'jacomax'

    # This has no releases, no tags, just a branch
    #input_username = 'davemckain'
    #input_reponame = 'asciimath-parser'

    github = Github(auth_token)
    user = github.get_user(input_username)
    repo = user.get_repo(input_reponame)
    github2cff = GitHubCffGuesser(repo)
    print(github2cff.to_cff_string())
