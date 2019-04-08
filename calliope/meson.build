sources = files(
  '__init__.py',
  '__main__.py',
  'cache.py',
  'cli.py',
  'config.py',
  'playlist.py',
)

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

# Sources for the whole 'calliope' module. This variable is appended to by the
# meson.build files inside the package subdirectories.
calliope_module_sources = sources

subdir('diff')
subdir('export')
subdir('import_')
subdir('shuffle')
subdir('stat')
subdir('sync')

if enable_lastfm
  subdir('lastfm')
endif

if enable_musicbrainz
  subdir('musicbrainz')
endif

if enable_play
  subdir('play')
endif

if enable_spotify
  subdir('spotify')
endif

if enable_suggest
  subdir('suggest')
endif

if enable_tracker
  subdir('tracker')
endif

if enable_web
  subdir('web')
  subdir('data/web/templates')
endif
