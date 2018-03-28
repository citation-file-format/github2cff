from gitlab import Gitlab
from pprint import pprint
import re

'''
FIXME: This is just a sketch at present!
'''

# FIXME: Put the GitHub auth token in the file below for now. Do NOT commit this file to git :-)
auth_token_file = 'auth_token.txt'

with open(auth_token_file, 'r') as f:
    auth_token = f.read().strip()

# TODO: These will become user-selectable inputs
# input_username = 'codemeta'
# input_reponame = 'codemeta'

# This has releases + a newer tag!
# Here we'd expect to take the last release rather than the last branch
#input_username = 'citation-file-to_cff_string'
#input_reponame = 'cff-converter-python'

# This has no releases, but lots of tags
#input_username = 'davemckain'
#input_reponame = 'jacomax'

# This has no releases, no tags, just a branch
#input_username = 'davemckain'
#input_reponame = 'asciimath-parser'

input_username = 'JosephThomasParker'
input_reponame = 'STORM'

###########################################################


def _debug_list(name, paginated_list):
    """Temporary to debug the contents of a PagninatedList object"""
    print("Debugging {}".format(name))
    for item in paginated_list:
        pprint(item)


class GitLabCffGuesser:
    """
    This class extracts (guesses?) CFF metadata from a GitLab repository id
    """

    def __init__(self, g, repo):
        self.g      = g
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
        result['title'] = self.g.getproject(self.repo)['name']
        result['authors'] = self._extract_contributors()
        self._extract_release_info(result)
        self.parsed = result

    def _extract_release_info(self, result):
        """
        This tries to extract data from the best possible release information.
        FIXME: Not implemented...
        """
#        releases = list(self.repo.get_releases())
#        tags = list(self.repo.get_tags())
#        if len(releases):
#            # Take most recent release
#            latest_release = releases[0]
#            pprint(latest_release)
#            result['version'] = latest_release.tag_name
#            result['release_date'] = self.to_cff_date(latest_release.created_at)
#        elif len(tags):
#            # Take most recent tag
#            latest_tag = tags[0]
#            result['version'] = latest_tag.name
#            result['release_date'] = self.to_cff_date(latest_tag.commit.commit.author.date)
#        else:
#            # No tags yet, so we'll take the last commit on the default branch
#            branch = repo.get_branch(repo.default_branch)
#            result['version'] = branch.commit.sha
#            result['release_date'] = self.to_cff_date(branch.commit.commit.author.date)

        result['version'] = 0.0
        result['release_date'] = self.to_cff_date("2018-03-28 15:01:00")
        
    def _parse_human_name(self, name):
        """
        FIXME: Yuck yuck yuck! This assumes everyone is called FIRST LAST!
        """
        bits = re.split(r'\s+', name)
        return ' '.join(bits[0:-1]), bits[-1]

    def _extract_contributors(self):
        """
        Extracts contributor information from this repository
        """
        result = []
        tmp = []
        first = True
        for r in self.g.getcontributors(self.repo, page=1, per_page=20):
            name = r['name']
            # GitLab offers no way of telling if contributor is human
            # Default to giving single name
            if first:
                result.append({
                        'name': name
                    })
                tmp.append(name)
                first = False

            else:
                if name not in tmp:
                    result.append({
                            'name': name
                        })
                    tmp.append(name)
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
        """
        parsed = self.as_dict()
        return '''
cff-version: 1.0.3
message: If you use this software, please cite it as below.        
title: {title}
version: {version}
{authors_formatted}date-released: {date_released}
repository-code: {repo_url}'''.format(
            title=parsed['title'],
            version=parsed['version'],
            authors_formatted=self._format_authors(),
            date_released=parsed['release_date'],
            repo_url=self.g.getproject(self.repo)['http_url_to_repo'],
                   )

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
gitlab = Gitlab('https://gitlab.com/', token=auth_token)
repo_id=4251096
gitlab2cff = GitLabCffGuesser(gitlab,repo_id)
print(gitlab2cff.to_cff_string())
