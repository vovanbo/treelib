__config_version__ = 1

GLOBALS = {
    'serializer': '{{major}}.{{minor}}.{{patch}}',
}

FILES = [
    {
        'path': 'ttree/__init__.py',
        'serializer': "__version__ = '{{ GLOBALS.serializer }}'"
    },
]

VERSION = ['major', 'minor', 'patch']

VCS = {
    'name': 'git',
    'commit_message': "Version updated from {{ current_version }} to {{ new_version }}",
}
