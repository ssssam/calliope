gnome = import('gnome')

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

install_data(
    sources,
    install_dir: join_paths(python_site_packages_dir, 'calliope', 'apps', 'viewer'))

resources = gnome.compile_resources('calliope-viewer', 'calliope-viewer.gresource.xml',
    gresource_bundle: true,
    install: true,
    install_dir: pkgdatadir)
