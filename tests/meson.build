tests = [
  'test_cache.py',
  'test_cli.py',
  'test_export.py',
  'test_import.py',
  'test_tracker.py',
]

pytest_env = environment()
pytest_env.set('CALLIOPE_MODULES_CONFIG', join_paths(top_build_dir, 'calliope', 'modules.json'))
# FIXME: doing 'prepend' twice seems to lose one of the values; possibly a
# bug in Meson 0.44.1..
pytest_env.prepend('PYTHONPATH', '@0@:@1@:@2@'.format(
  pytest_workdir,
  join_paths(pytest_workdir, 'subprojects', 'lastfmclient'),
  join_paths(pytest_workdir, 'subprojects', 'tracker-app-domain')))

foreach t: tests
  test(t, pytest,
    args: join_paths('tests', t),
    env: pytest_env,
    workdir: pytest_workdir)
endforeach
