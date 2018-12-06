tests = [
  'test_cache.py',
  'test_cli.py',
  'test_export.py',
  'test_import.py',
  'test_tracker.py',
]

foreach t: tests
  test(t, run_from_source_tree,
    args: [top_source_dir, top_build_dir, pytest.path(), join_paths('tests', t)],
    # We can put a pytest.ini file in this directory to configure pytest.
    workdir: top_source_dir)
endforeach
