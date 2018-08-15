project('calliope')

subproject('tracker-app-domain')

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
  'lightfm',
  'musicbrainzngs',
  'spotipy',
]

setup_requires = [
]

test_requires = [
  'mutagen',
]

missing_dependency_errors = []

message('Checking for Python dependencies')
modules_check = run_command(python, 'meson-python-packages-check', install_requires + setup_requires + test_requires)
if modules_check.returncode() != 0
  error('Python dependency requirements are not satisfied:\n' + modules_check.stderr().strip())
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

subdir('calliope')

subdir('tests')
