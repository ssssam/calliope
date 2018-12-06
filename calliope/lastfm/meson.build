sources = files(
  '__init__.py',
  'history.py',
  'lastexport.py',
)

migrations = files('migrations/0001.init.py')

python.install_sources(sources,
    pure: false,
    subdir: join_paths('calliope', 'lastfm'))

python.install_sources(migrations,
    pure: false,
    subdir: join_paths('calliope', 'lastfm', 'migrations'))

calliope_module_sources = sources + migrations
