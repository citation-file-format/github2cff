from github import Github
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

###########################################################


def _debug_list(name, paginated_list):
    '''Temporary to debug the contents of a PagninatedList object'''
    print("Debugging {}".format(name))
    for item in paginated_list:
        pprint(item)


class CffAuthor:
    """
    FIXME: Downgrade this to a dictionary, as that's what we're returning elsewhere
    """
    def __init__(self, family_names, given_names, entity_name=None):
        self.family_names = family_names
        self.given_names = given_names
        self.entity_name = entity_name

    def format(self):
        if self.entity_name:
            return 'name: {}'.format(self.entity_name)
        else:
            return 'family-names: {}\ngiven-names: {}'.format(
                self.family_names, self.given_names
            )


class GitHubCffGuesser:
    def __init__(self, repo):
        self.repo = repo
        self.parsed = None

    def run(self):
        result = dict()
        result['title'] = self.repo.name
        result['contributors'] = self._extract_contributors()
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
            pprint(latest_release)
            result['version'] = latest_release.tag_name
            result['release_date'] = self.to_cff_date(latest_release.created_at)
        elif len(tags):
            # Take most recent tag
            latest_tag = tags[0]
            result['version'] = latest_tag.name
            result['release_date'] = self.to_cff_date(latest_tag.commit.commit.author.date)
        else:
            # No tags yet, so we'll take the last commit on the default branch
            branch = repo.get_branch(repo.default_branch)
            result['version'] = branch.commit.sha
            result['release_date'] = self.to_cff_date(branch.commit.commit.author.date)

    def _parse_human_name(self, name):
        """
        FIXME: Yuck yuck yuck! This assumes everyone is called FIRST LAST!
        """
        bits = re.split(r'\s+', name)
        return ' '.join(bits[0:-1]), bits[-1]

    def _extract_contributors(self):
        result = []
        for contributor in self.repo.get_contributors():
            name = contributor.name
            if contributor.type == 'User':
                first, last = self._parse_human_name(name)
                result.append(CffAuthor(first, last, None))
            else:
                result.append(CffAuthor(None, None, name))
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
        self._ensure_run()
        return self.parsed

    def format(self):
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
            repo_url=self.repo.html_url,
                   )

    def _format_authors(self):
        formatted_items = []
        for a in self.as_dict()['contributors']:
            if a.entity_name:
                formatted_items.append('  - name: {}\n'.format(a.entity_name))
            else:
                formatted_items.append(
                    '  - family-names: {}\n    given-names: {}\n'.format(a.family_names, a.given_names))
        return 'authors:\n' + ''.join(formatted_items)


g = Github(auth_token)
u = g.get_user(input_username)
repo = u.get_repo(input_reponame)
g = GitHubCffGuesser(repo)
print(g.format())


