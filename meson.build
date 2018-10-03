project('calliope')

if get_option('tracker')
  subproject('tracker-app-domain')
endif

###############################################################################
# Python dependencies
###############################################################################

python = find_program('python3', required: true)

python_version_check = run_command(python, '-c', 'import sys; sys.stdout.write("%d.%d" % (sys.version_info[0], sys.version_info[1]))')
if python_version_check.returncode() != 0
  error('Unable to detect Python version: ' + result.stdout() + result.stderr())
endif
python_version = python_version_check.stdout()

if not python_version.version_compare('>= 3.5')
  error('Python 3.5 or newer is required.')
endif

python_name = 'python' + python_version
python_site_packages_dir = join_paths(get_option('prefix'), get_option('libdir'), python_name, 'site-packages')

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
  install_requires += ['lastfmclient']
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

setup_requires = [
]

test_requires = [
  'mutagen',
]

missing_dependency_errors = []

message('Checking for Python dependencies')
modules_check = run_command(python, 'meson-python-packages-check', install_requires + setup_requires)
if modules_check.returncode() != 0
  error('Python dependency requirements are not satisfied:\n' + modules_check.stderr().strip())
endif

if get_option('testsuite')
  message('Checking for Python test suite dependencies')
  modules_check = run_command(python, 'meson-python-packages-check', test_requires)
  if modules_check.returncode() != 0
    error('Test suite dependency requirements are not satisfied:\n' + modules_check.stderr().strip())
  endif
endif

pytest = find_program('pytest-3', required: false)
# We configure pytest through a pytest.ini file in this directory, so as
# long as we set the workdir correctly it "just works" when run by Meson.
pytest_workdir = meson.current_source_dir()

###############################################################################
# Configuration
###############################################################################

cdata = configuration_data()
cdata.set('pythondir', python_site_packages_dir)
cdata.set10('enable_lastfm', get_option('lastfm'))
cdata.set10('enable_musicbrainz', get_option('musicbrainz'))
cdata.set10('enable_play', get_option('play'))
cdata.set10('enable_spotify', get_option('spotify'))
cdata.set10('enable_suggest', get_option('suggest'))
cdata.set10('enable_tracker', get_option('tracker'))

top_build_dir = meson.current_build_dir()

subdir('calliope')

subdir('tests')

# Install the bundled lastfmclient library.
#
# Theoretically this could conflict with an existing user-installed version,
# but the upstream version doesn't work with Python 3 so it's unlikely to be
# part of any existing Python 3 installations.
install_subdir(
    'subprojects/lastfmclient/lastfmclient',
    install_dir: join_paths(python_site_packages_dir))
