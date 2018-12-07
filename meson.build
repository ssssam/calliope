project('calliope',
        meson_version: '>= 0.46')

if get_option('tracker')
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
  'pyxdg',
]

if get_option('lastfm')
  install_requires += ['yoyo-migrations']
endif

if get_option('musicbrainz')
  install_requires += ['musicbrainzngs']
endif

if get_option('spotify')
  install_requires += ['spotipy']
endif

if get_option('suggest')
  install_requires += ['lightfm']
endif

if get_option('web')
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
endif

pytest = find_program('pytest-3')

###############################################################################
# Configuration
###############################################################################

localedir = join_paths(get_option('prefix'), get_option('localedir'))
pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), 'tagcloud')

cdata = configuration_data()
cdata.set10('enable_lastfm', get_option('lastfm'))
cdata.set10('enable_musicbrainz', get_option('musicbrainz'))
cdata.set10('enable_play', get_option('play'))
cdata.set10('enable_spotify', get_option('spotify'))
cdata.set10('enable_suggest', get_option('suggest'))
cdata.set10('enable_tracker', get_option('tracker'))
cdata.set10('enable_web', get_option('web'))
cdata.set('localedir', localedir)
cdata.set('pkgdatadir', pkgdatadir)
cdata.set('pythonsitepackagesdir', python.get_install_dir(pure: false))

top_source_dir = meson.current_source_dir()
top_build_dir = meson.current_build_dir()

run_from_source_tree = find_program('scripts/run_from_source_tree', required: true)

subdir('calliope')

if get_option('viewer')
  subdir('apps/viewer')
endif

subdir('tests')

if get_option('docs')
  subdir('docs')
endif

if get_option('lastfm')
  # Install the bundled lastfmclient library.
  #
  # Theoretically this could conflict with an existing user-installed version,
  # but the upstream version doesn't work with Python 3 so it's unlikely to be
  # part of any existing Python 3 installations.
  install_subdir(
      'subprojects/lastfmclient/lastfmclient',
      install_dir: python.get_install_dir(pure: false))
endif
