sphinx_sources = [
  'conf.py',
  'index.rst',
  'reference.rst',
  'use-cases.rst',
  'use-cases/copy-onto-portable-device.rst',
  'use-cases/create-mix.rst',
  'use-cases/follow-top-artists-on-twitter.rst',
  'use-cases/never-listened.rst',
  'use-cases/top-artists.rst',
  'use-cases/what-to-buy.rst',
]

docs_html = custom_target('docs',
  build_by_default: true,
  command: [sphinx_build, '-M', 'html', meson.current_source_dir(),
            meson.current_build_dir()],
  depend_files: sphinx_sources,
  # We only list one output.
  output: ['html']
)
