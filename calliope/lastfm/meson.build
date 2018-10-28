lastfm_sources = [
  '__init__.py',
  'history.py',
  'lastexport.py',
]

lastfm_migrations = ['migrations/0001.init.py']

install_data(
    lastfm_sources,
    install_dir: join_paths(python_site_packages_dir, 'calliope', 'lastfm'))

install_data(
    lastfm_migrations,
    install_dir: join_paths(python_site_packages_dir, 'calliope', 'lastfm', 'migrations'))
