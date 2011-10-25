APPNAME = 'calliope'
VERSION = '0.3.0'
top = '.'
bld = 'build'

# FIXME: waf API inconsistency
vala_min_version = (0,14,0)

# 2.26 for GDateTime (Charango)
glib_min_version = '2.26.0'

redland_min_version = '1.0.10'

# Optional deps
gtk_min_version = '3.0.0'

test_execution_order = []

import os
import subprocess
from waflib import Logs
from waflib import Options

def options (opt):
	opt.load ('compiler_c vala glib2')

	opt.add_option ('--stable', action = 'store_true', default = False,
	                help = 'Declare build stable (ie. not beta).', dest = "stable")

def configure(conf):
	conf.load ('compiler_c vala glib2')

	# (Charango) ensure sizeof(int) >= 4, or Charango.Value will break

	conf.check_tool ('gcc glib2')
	conf.check_vala (min_version = vala_min_version)

	if Options.options.stable:
		conf.env.append_value ('CFLAGS', '-O3')
	else:
		conf.env.append_value ('VALAFLAGS', '-g')
		conf.env.append_value ('CFLAGS', '-g')
		conf.env.append_value ('CFLAGS', '-O0')


	conf.check_cfg (package         = 'gio-2.0',
	                uselib_store    = 'GIO',
	                atleast_version = glib_min_version,
	                args            = '--cflags --libs',
	                mandatory       = True)

	# Charango deps
	conf.check_cfg (package         = 'redland',
	                uselib_store    = 'REDLAND',
	                atleast_version = redland_min_version,
	                args            = '--cflags --libs',
	                mandatory       = True)

	conf.check_cfg (package         = 'raptor2',
                        uselib_store    = 'RAPTOR',
                        args            = '--cflags --libs',
                        mandatory       = True)

	conf.check_cfg (package         = 'gtk+-3.0',
	                uselib_store    = 'GTK',
	                atleast_version = gtk_min_version,
	                args            = '--cflags --libs',
	                mandatory       = False)

	conf.env['GTESTER'] = conf.find_program('gtester')

	conf.define ("SRCDIR", os.path.abspath(top));
	#if sys.platform=='win32':
	#	conf.env.append_value ('CFLAGS', '-mms-bitfields')

	mode = 'normal'
	print
	print "Building Calliope version %s in %s mode." % (VERSION, mode)


def build(bld):
	bld.recurse ('charango')


def check (bld):
	# Make sure the tests are up to date, run 'check' after the build
	build (bld)
	bld.add_post_fun (check_action)

def check_action (bld):
	# Run tests through gtester
	#
	test_nodes = []
	for test in test_execution_order:
		test_obj = bld.get_tgen_by_name (test)

		if not hasattr (test_obj,'unit_test') or not getattr(test_obj, 'unit_test'):
			continue

		file_node = test_obj.target.abspath()
		test_nodes.append (file_node)

	gtester_run (bld, test_nodes);

from waflib.Build import BuildContext
class check_context(BuildContext):
	cmd = 'check'
	fun = 'check'


def gtester_run (bld, test_nodes):
	if not test_nodes:
		return

	gtester_params = [bld.env['GTESTER']]
	gtester_params.append ('--verbose');

	# A little black magic to make the tests run
	gtester_env = os.environ
	gtester_env['LD_LIBRARY_PATH'] = gtester_env.get('LD_LIBRARY_PATH', '') + \
	                                   ':' + bld.path.get_bld().abspath()

	for test in test_nodes:
		gtester_params.append (test)

	if Logs.verbose > 1:
		print gtester_params
	pp = subprocess.Popen (gtester_params,
	                       env = gtester_env)
	result = pp.wait ()
