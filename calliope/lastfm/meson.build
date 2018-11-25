lastfm_sources = [
  '__init__.py',
  'history.py',
  'lastexport.py',
]

lastfm_migrations = ['migrations/0001.init.py']

python.install_sources(lastfm_sources,
    pure: false,
    subdir: join_paths('calliope', 'lastfm'))

python.install_sources(lastfm_migrations,
    pure: false,
    subdir: join_paths('calliope', 'lastfm', 'migrations'))
