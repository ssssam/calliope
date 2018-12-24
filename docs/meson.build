sphinx_sources = [
  'conf.py',
  'index.rst',
  'format.rst',
  'reference.rst',
  'use-cases.rst',
  'use-cases/copy-onto-portable-device.rst',
  'use-cases/create-mix.rst',
  'use-cases/follow-top-artists-on-twitter.rst',
  'use-cases/listen-history.rst',
  'use-cases/never-listened.rst',
  'use-cases/selecting-from-a-collection.rst',
  'use-cases/top-artists.rst',
  'use-cases/what-to-buy.rst',
]

docs_html = custom_target('docs',
  build_by_default: true,
  command: [run_from_source_tree, top_source_dir, top_build_dir,
            sphinx_build, '-M', 'html', meson.current_source_dir(),
            meson.current_build_dir(), '-W'],
  depend_files: sphinx_sources + calliope_module_sources,
  # We only list one output.
  output: ['html']
)
