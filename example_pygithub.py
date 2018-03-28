from github import Github
from pprint import pprint
import re

'''
FIXME: This is just a sketch at present!
'''

# TODO: Temporary auth token for initial work. Will be revoked shortly...
auth_token  = 'ff4a6942deac6d2c116d2fcf357068952eb71419'

# TODO: These will become user-selectable inputs
github_user = 'davemckain'
user_repo   = 'jacomax'

###########################################################

g = Github('ff4a6942deac6d2c116d2fcf357068952eb71419')
u = g.get_user('davemckain')
repo = u.get_repo('jacomax')

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

def to_date(datetime):
    '''Transforms a GitHub YYYY-MM-DD HH:MM:SS into the CFF date'''
    return str(datetime)[0:10]

_debug_list("Contributors", repo.get_contributors())


def parse_human_name(name):
    bits = re.split(r'\s+', name)
    return ' '.join(bits[0:-1]), bits[-1]


def extract_contributors(repo):
    result = []
    for contributor in repo.get_contributors():
        name = contributor.name
        print('Doing: ' + name)
        if contributor.type == 'User':
            first, last = parse_human_name(name)
            result.append(CffAuthor(first, last, None))
        else:
            result.append(CffAuthor(None, None, name))
    return result


print(extract_contributors(repo))





def extract_title(repo):
    return repo.name


# FIXME: This needs to be a lot more clever!
def extract_version(repo):
    latest_tag = _get_latest_tag(repo)
    return latest_tag.name


def extract_release_date(repo):
    latest_tag = _get_latest_tag(repo)
    return to_date(latest_tag.commit.committer.created_at)


def _get_latest_tag(repo):
    tags = list(repo.get_tags())
    assert(len(tags) > 0)
    return tags[0]

def format_authors(cff_authors):
    formatted_items = []
    for a in cff_authors:
        if a.entity_name:
            formatted_items.append('  - name: {}\n'.format(a.entity_name))
        else:
            formatted_items.append('  - family-names: {}\n    given-names: {}\n'.format(a.family_names, a.given_names))
    return 'authors:\n' + ''.join(formatted_items)


print('''
cff-version: 1.0.3
message: If you use this software, please cite it as below.
title: {title}
version: {version}
{authors_formatted}date-released: {date_released}
repository-code: {repo_url}
'''.format(title=extract_title(repo),
           version=extract_version(repo),
           authors_formatted=format_authors(extract_contributors(repo)),
           date_released=extract_release_date(repo),
           repo_url=repo.html_url,
           ))