project('calliope')

subproject('tracker-app-domain')

python = find_program('python3', required: true)

# We need to check for Python dependencies; but it's not possible with
# Meson until https://github.com/mesonbuild/meson/issues/2377 is fixed

python_version_check = run_command(python, '-c', 'import sys; sys.stdout.write("%d.%d" % (sys.version_info[0], sys.version_info[1]))')
if python_version_check.returncode() != 0
  error('Unable to detect Python version: ' + result.stdout() + result.stderr())
endif
python_version = python_version_check.stdout()

python_name = 'python' + python_version
python_site_packages_dir = join_paths(get_option('prefix'), get_option('libdir'), python_name, 'site-packages')

cdata = configuration_data()
cdata.set('pythondir', python_site_packages_dir)

subdir('calliope')

pytest = find_program('pytest-3')

pytest_env = environment()
# FIXME: doing 'prepend' twice seems to lose one of the values; possibly a
# bug in Meson 0.44.1..
pytest_env.prepend('PYTHONPATH', '@0@:@1@'.format(
    meson.current_source_dir(),
    join_paths(meson.current_source_dir(), 'subprojects', 'tracker-app-domain')))
test('pytest', pytest,
    env: pytest_env,
    workdir: meson.current_source_dir())
