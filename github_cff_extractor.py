from github import Github
from pprint import pprint
import re

'''
FIXME: This is just a sketch at present!
'''

# TODO: Temporary auth token for initial work. Will be revoked shortly...
auth_token  = 'ff4a6942deac6d2c116d2fcf357068952eb71419'

# TODO: These will become user-selectable inputs
input_username = 'codemeta'
input_reponame = 'codemeta'

###########################################################


class CffAuthor:
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

def _debug_list(name, paginated_list):
    '''Temporary to debug the contents of a PagninatedList object'''
    print("Debugging {}".format(name))
    for item in paginated_list:
        pprint(item)




class GitHubCffGuesser:
    def __init__(self, repo):
        self.repo = repo
        self.parsed = None

    def run(self):
        result = dict()
        result['title'] = self.repo.name
        result['version'] = self._extract_version()
        result['release_date'] = self._extract_release_date()
        result['contributors'] = self._extract_contributors()
        self.parsed = result

    # FIXME: This only handles one logic branch at present!
    def _extract_version(self):
        latest_tag = self._get_latest_tag()
        return latest_tag.name

    # FIXME: This is not returning the right date at present!
    # FIXME: This proably needs to be done at the same time as
    # _extract_version() as we need to deal with multiple code branches...
    def _extract_release_date(self):
        latest_tag = self._get_latest_tag()
        return self.to_cff_date(latest_tag.commit.committer.created_at)

    def _get_latest_tag(self):
        tags = list(self.repo.get_tags())
        assert (len(tags) > 0)
        return tags[0]

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