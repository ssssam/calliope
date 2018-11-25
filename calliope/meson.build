sources = [
  '__init__.py',
  '__main__.py',
  'cache.py',
  'config.py',
  'cmd_diff.py',
  'cmd_export.py',
  'cmd_import.py',
  'cmd_shuffle.py',
  'cmd_stat.py',
  'cmd_sync.py',
  'playlist.py',
]

if get_option('lastfm')
  sources += ['cmd_lastfm.py']
  subdir('lastfm')
endif

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

if get_option('web')
  sources += ['cmd_web.py']
endif

python.install_sources(
    sources,
    pure: false,
    subdir: 'calliope')

configure_file(
    input: 'modules.json.in',
    output: 'modules.json',
    configuration: cdata,
    install_dir: join_paths(python.get_install_dir(pure: false), 'calliope'))

configure_file(
    input: 'main.py.in',
    output: 'cpe',
    configuration: cdata,
    install_dir: get_option('bindir'))

if get_option('web')
  subdir('data/web/templates')
endif
