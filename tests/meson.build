run_target('pylint',
  command: [run_from_source_tree, top_source_dir, top_build_dir, pylint.path(), '--rcfile', join_paths(top_source_dir, 'pylintrc')] + calliope_module_sources)

tests = [
  'test_cache.py',
  'test_cli.py',
  'test_core.py',
  'test_export.py',
  'test_import_pls.py',
  'test_import_xspf_jspf.py',
  'test_tracker.py',
]

foreach t: tests
  test(t, run_from_source_tree,
    args: [top_source_dir, top_build_dir, pytest.path(), join_paths('tests', t)],
    # We can put a pytest.ini file in this directory to configure pytest.
    workdir: top_source_dir)
endforeach
