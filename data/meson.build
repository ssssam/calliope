# Generate metadata for Python 'setuptools' packaging. This makes
# `pkg_resources.require('calliope')` work as expected.
#
# See:
#   <https://setuptools.readthedocs.io/en/latest/formats.html>
#   <https://packaging.python.org/specifications/core-metadata/>
#
configure_file(
  input: 'calliope.egg-info.in',
  output: 'calliope-@0@-py@1@.egg-info'.format(meson.project_version(), python.language_version()),
  configuration: cdata,
  install: true,
  install_dir: python.get_install_dir(pure: false))
