sources = [
  '__main__.py',
  'cache.py',
  'config.py',
  'cmd_export.py',
  'cmd_import.py',
  'cmd_shuffle.py',
  'cmd_stat.py',
  'cmd_sync.py',
  'cmd_web.py',
  'playlist.py',
]

if get_option('musicbrainz')
  sources += ['cmd_musicbrainz.py']
endif

if get_option('play')
  sources += ['cmd_play.py']
endif

if get_option('spotify')
  sources += ['cmd_spotify.py']
endif

if get_option('suggest')
  sources += ['cmd_suggest.py']
endif

if get_option('tracker')
  sources += ['cmd_tracker.py']
endif

install_data(
    sources,
    install_dir: join_paths(python_site_packages_dir, 'calliope'))

configure_file(
    input: '__init__.py.in',
    output: '__init__.py',
    configuration: cdata,
    install_dir: join_paths(python_site_packages_dir, 'calliope'))

configure_file(
    input: 'main.py.in',
    output: 'cpe',
    configuration: cdata,
    install_dir: get_option('bindir'))

subdir('data/web/templates')
