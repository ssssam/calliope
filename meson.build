project('calliope',
        meson_version: '>= 0.47')

# Process the feature dependecies.
#
# We use the 'feature' option where possible because it allows users to
# easy opt-in to every feature (set auto_features=enabled) or opt-out of
# every feature (set auto_features=disabled).
#
# Since Meson doesn't natively support Python module dependencies yet
# (see https://github.com/mesonbuild/meson/issues/2377), we have to 'decode'
# the value of each option manually.
#
enable_lastfm = (get_option('lastfm').auto() or get_option('lastfm').enabled())
enable_musicbrainz = (get_option('musicbrainz').auto() or get_option('musicbrainz').enabled())
enable_play = (get_option('play').auto() or get_option('play').enabled())
enable_spotify = (get_option('spotify').auto() or get_option('spotify').enabled())
enable_suggest = (get_option('suggest').auto() or get_option('suggest').enabled())
enable_tracker = (get_option('tracker').auto() or get_option('tracker').enabled())
enable_viewer_app = (get_option('viewer').auto() or get_option('viewer').enabled())
enable_web = (get_option('web').auto() or get_option('web').enabled())

if enable_tracker
  subproject('tracker-app-domain')
endif

###############################################################################
# Python dependencies
###############################################################################

pymod = import('python')

python = pymod.find_installation('python3')

if not python.language_version().version_compare('>= 3.5')
  error('Python 3.5 or newer is required.')
endif

# FIXME: We check manually for our Python dependencies as Meson doesn't
# support doing so yet. See https://github.com/mesonbuild/meson/issues/2377
message('Checking for setuptools (for pkg_resources)')
setuptools_check = run_command(python, '-c', 'import pkg_resources')
if setuptools_check.returncode() != 0
  error('Python Setuptools was not found; the pkg_resources module is required.\n' +
        setuptools_check.stderr().strip())
endif

install_requires = [
  'click',
  'parsedatetime',
  'pyxdg',
  'splitstream',
]

if enable_lastfm
  install_requires += ['yoyo-migrations']
endif

if enable_musicbrainz
  install_requires += ['musicbrainzngs']
endif

if enable_spotify
  install_requires += ['spotipy']
endif

if enable_suggest
  install_requires += ['lightfm']
endif

if enable_web
  install_requires += ['jinja2']
endif

setup_requires = [
]

test_requires = [
  'mutagen', 'pytest-benchmark'
]

doc_requires = [
  'sphinx', 'sphinx-click',
]

missing_dependency_errors = []

message('Checking for Python dependencies')
modules_check = run_command(python, 'meson-python-packages-check', install_requires + setup_requires)
if modules_check.returncode() != 0
  error('Python dependency requirements are not satisfied:\n' + modules_check.stderr().strip())
endif

if get_option('docs')
  message('Checking for Python documentation dependencies')
  modules_check = run_command(python, 'meson-python-packages-check', doc_requires)
  if modules_check.returncode() != 0
    error('Documentation dependency requirements are not satisfied:\n' + modules_check.stderr().strip())
  endif

  sphinx_build = find_program('sphinx-build-3', 'sphinx-build', required: true)
endif

if get_option('testsuite')
  message('Checking for Python test suite dependencies')
  modules_check = run_command(python, 'meson-python-packages-check', test_requires)
  if modules_check.returncode() != 0
    error('Test suite dependency requirements are not satisfied:\n' + modules_check.stderr().strip())
  endif

  pylint = find_program('pylint-3', 'pylint')

  pytest = find_program('pytest-3')
endif

###############################################################################
# Configuration
###############################################################################

localedir = join_paths(get_option('prefix'), get_option('localedir'))
pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), 'tagcloud')

cdata = configuration_data()
cdata.set10('enable_lastfm', enable_lastfm)
cdata.set10('enable_musicbrainz', enable_musicbrainz)
cdata.set10('enable_play', enable_play)
cdata.set10('enable_spotify', enable_spotify)
cdata.set10('enable_suggest', enable_suggest)
cdata.set10('enable_tracker', enable_tracker)
cdata.set10('enable_web', enable_web)
cdata.set('localedir', localedir)
cdata.set('pkgdatadir', pkgdatadir)
cdata.set('pythonsitepackagesdir', python.get_install_dir(pure: false))

top_source_dir = meson.current_source_dir()
top_build_dir = meson.current_build_dir()

run_from_source_tree = find_program('scripts/run_from_source_tree', required: true)

subdir('calliope')

if enable_viewer_app
  subdir('apps/viewer')
endif

if get_option('testsuite')
  subdir('tests')
endif

if get_option('docs')
  subdir('docs')
endif

if enable_lastfm
  # Install the bundled lastfmclient library.
  #
  # Theoretically this could conflict with an existing user-installed version,
  # but the upstream version doesn't work with Python 3 so it's unlikely to be
  # part of any existing Python 3 installations.
  install_subdir(
      'subprojects/lastfmclient/lastfmclient',
      install_dir: python.get_install_dir(pure: false))
endif
