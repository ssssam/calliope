gnome = import('gnome')

glib = dependency('glib-2.0')

sources = [
    '__init__.py',
    'app.py',
    'mainwindow.py',
    'playlistbox.py',
    'playlistmodel.py',
]

viewer_script = configure_file(
    input: 'main.py.in',
    output: 'calliope-viewer',
    configuration: cdata,
    install_dir: get_option('bindir'))

python.install_sources(
    sources,
    subdir: join_paths('calliope', 'apps', 'viewer'))

resources = gnome.compile_resources('calliope-viewer', 'calliope-viewer.gresource.xml',
    gresource_bundle: true,
    install: true,
    install_dir: pkgdatadir)
