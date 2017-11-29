
sources = [
  '__init__.py',
  'config.py',
  'cmd_export.py',
  'cmd_import.py',
  'cmd_musicbrainz.py',
  'cmd_play.py',
  'cmd_spotify.py',
  'cmd_stat.py',
  'cmd_sync.py',
  'cmd_tracker.py',
]

install_data(
    sources,
    install_dir: join_paths(python_site_packages_dir, 'calliope'))

configure_file(
    input: 'main.py.in',
    output: 'cpe',
    configuration: cdata,
    install_dir: get_option('bindir'))
