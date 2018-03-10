from setuptools import setup

setup(
    name='FriendorFoe',
    version='v1.0',
    packages=['venv.Lib.distutils', 'venv.Lib.encodings', 'venv.Lib.importlib', 'venv.Lib.collections',
              'venv.Lib.site-packages.pip', 'venv.Lib.site-packages.pip.req', 'venv.Lib.site-packages.pip.vcs',
              'venv.Lib.site-packages.pip.utils', 'venv.Lib.site-packages.pip.compat',
              'venv.Lib.site-packages.pip.models', 'venv.Lib.site-packages.pip._vendor',
              'venv.Lib.site-packages.pip._vendor.distlib', 'venv.Lib.site-packages.pip._vendor.distlib._backport',
              'venv.Lib.site-packages.pip._vendor.colorama', 'venv.Lib.site-packages.pip._vendor.html5lib',
              'venv.Lib.site-packages.pip._vendor.html5lib._trie',
              'venv.Lib.site-packages.pip._vendor.html5lib.filters',
              'venv.Lib.site-packages.pip._vendor.html5lib.treewalkers',
              'venv.Lib.site-packages.pip._vendor.html5lib.treeadapters',
              'venv.Lib.site-packages.pip._vendor.html5lib.treebuilders', 'venv.Lib.site-packages.pip._vendor.lockfile',
              'venv.Lib.site-packages.pip._vendor.progress', 'venv.Lib.site-packages.pip._vendor.requests',
              'venv.Lib.site-packages.pip._vendor.requests.packages',
              'venv.Lib.site-packages.pip._vendor.requests.packages.chardet',
              'venv.Lib.site-packages.pip._vendor.requests.packages.urllib3',
              'venv.Lib.site-packages.pip._vendor.requests.packages.urllib3.util',
              'venv.Lib.site-packages.pip._vendor.requests.packages.urllib3.contrib',
              'venv.Lib.site-packages.pip._vendor.requests.packages.urllib3.packages',
              'venv.Lib.site-packages.pip._vendor.requests.packages.urllib3.packages.ssl_match_hostname',
              'venv.Lib.site-packages.pip._vendor.packaging', 'venv.Lib.site-packages.pip._vendor.cachecontrol',
              'venv.Lib.site-packages.pip._vendor.cachecontrol.caches',
              'venv.Lib.site-packages.pip._vendor.webencodings', 'venv.Lib.site-packages.pip._vendor.pkg_resources',
              'venv.Lib.site-packages.pip.commands', 'venv.Lib.site-packages.pip.operations',
              'venv.Lib.site-packages.mako', 'venv.Lib.site-packages.mako.ext', 'venv.Lib.site-packages.past',
              'venv.Lib.site-packages.past.tests', 'venv.Lib.site-packages.past.types',
              'venv.Lib.site-packages.past.utils', 'venv.Lib.site-packages.past.builtins',
              'venv.Lib.site-packages.past.translation', 'venv.Lib.site-packages.pytz', 'venv.Lib.site-packages.yaml',
              'venv.Lib.site-packages.numpy', 'venv.Lib.site-packages.numpy.ma',
              'venv.Lib.site-packages.numpy.ma.tests', 'venv.Lib.site-packages.numpy.doc',
              'venv.Lib.site-packages.numpy.fft', 'venv.Lib.site-packages.numpy.fft.tests',
              'venv.Lib.site-packages.numpy.lib', 'venv.Lib.site-packages.numpy.lib.tests',
              'venv.Lib.site-packages.numpy.core', 'venv.Lib.site-packages.numpy.core.tests',
              'venv.Lib.site-packages.numpy.f2py', 'venv.Lib.site-packages.numpy.f2py.tests',
              'venv.Lib.site-packages.numpy.tests', 'venv.Lib.site-packages.numpy.compat',
              'venv.Lib.site-packages.numpy.linalg', 'venv.Lib.site-packages.numpy.linalg.tests',
              'venv.Lib.site-packages.numpy.random', 'venv.Lib.site-packages.numpy.random.tests',
              'venv.Lib.site-packages.numpy.testing', 'venv.Lib.site-packages.numpy.testing.tests',
              'venv.Lib.site-packages.numpy.testing.nose_tools', 'venv.Lib.site-packages.numpy.distutils',
              'venv.Lib.site-packages.numpy.distutils.tests', 'venv.Lib.site-packages.numpy.distutils.command',
              'venv.Lib.site-packages.numpy.distutils.fcompiler', 'venv.Lib.site-packages.numpy.matrixlib',
              'venv.Lib.site-packages.numpy.matrixlib.tests', 'venv.Lib.site-packages.numpy.polynomial',
              'venv.Lib.site-packages.numpy.polynomial.tests', 'venv.Lib.site-packages.wheel',
              'venv.Lib.site-packages.wheel.tool', 'venv.Lib.site-packages.wheel.signatures',
              'venv.Lib.site-packages.future', 'venv.Lib.site-packages.future.moves',
              'venv.Lib.site-packages.future.moves.dbm', 'venv.Lib.site-packages.future.moves.html',
              'venv.Lib.site-packages.future.moves.http', 'venv.Lib.site-packages.future.moves.test',
              'venv.Lib.site-packages.future.moves.urllib', 'venv.Lib.site-packages.future.moves.xmlrpc',
              'venv.Lib.site-packages.future.moves.tkinter', 'venv.Lib.site-packages.future.tests',
              'venv.Lib.site-packages.future.types', 'venv.Lib.site-packages.future.utils',
              'venv.Lib.site-packages.future.builtins', 'venv.Lib.site-packages.future.backports',
              'venv.Lib.site-packages.future.backports.html', 'venv.Lib.site-packages.future.backports.http',
              'venv.Lib.site-packages.future.backports.test', 'venv.Lib.site-packages.future.backports.email',
              'venv.Lib.site-packages.future.backports.email.mime', 'venv.Lib.site-packages.future.backports.urllib',
              'venv.Lib.site-packages.future.backports.xmlrpc', 'venv.Lib.site-packages.future.standard_library',
              'venv.Lib.site-packages.pygame', 'venv.Lib.site-packages.pygame.docs',
              'venv.Lib.site-packages.pygame.gp2x', 'venv.Lib.site-packages.pygame.tests',
              'venv.Lib.site-packages.pygame.tests.test_utils', 'venv.Lib.site-packages.pygame.tests.run_tests__tests',
              'venv.Lib.site-packages.pygame.tests.run_tests__tests.all_ok',
              'venv.Lib.site-packages.pygame.tests.run_tests__tests.exclude',
              'venv.Lib.site-packages.pygame.tests.run_tests__tests.timeout',
              'venv.Lib.site-packages.pygame.tests.run_tests__tests.failures1',
              'venv.Lib.site-packages.pygame.tests.run_tests__tests.everything',
              'venv.Lib.site-packages.pygame.tests.run_tests__tests.incomplete',
              'venv.Lib.site-packages.pygame.tests.run_tests__tests.print_stderr',
              'venv.Lib.site-packages.pygame.tests.run_tests__tests.print_stdout',
              'venv.Lib.site-packages.pygame.tests.run_tests__tests.infinite_loop',
              'venv.Lib.site-packages.pygame.tests.run_tests__tests.incomplete_todo',
              'venv.Lib.site-packages.pygame.threads', 'venv.Lib.site-packages.pygame.examples',
              'venv.Lib.site-packages.serial', 'venv.Lib.site-packages.iso8601', 'venv.Lib.site-packages.dateutil',
              'venv.Lib.site-packages.dateutil.tz', 'venv.Lib.site-packages.dateutil.zoneinfo',
              'venv.Lib.site-packages.markdown', 'venv.Lib.site-packages.markdown.extensions',
              'venv.Lib.site-packages.markupsafe', 'venv.Lib.site-packages.matplotlib',
              'venv.Lib.site-packages.matplotlib.tri', 'venv.Lib.site-packages.matplotlib.axes',
              'venv.Lib.site-packages.matplotlib.cbook', 'venv.Lib.site-packages.matplotlib.style',
              'venv.Lib.site-packages.matplotlib.compat', 'venv.Lib.site-packages.matplotlib.testing',
              'venv.Lib.site-packages.matplotlib.testing._nose',
              'venv.Lib.site-packages.matplotlib.testing._nose.plugins',
              'venv.Lib.site-packages.matplotlib.testing.jpl_units', 'venv.Lib.site-packages.matplotlib.backends',
              'venv.Lib.site-packages.matplotlib.backends.qt_editor', 'venv.Lib.site-packages.matplotlib.sphinxext',
              'venv.Lib.site-packages.matplotlib.projections', 'venv.Lib.site-packages.setuptools',
              'venv.Lib.site-packages.setuptools.extern', 'venv.Lib.site-packages.setuptools.command',
              'venv.Lib.site-packages.libfuturize', 'venv.Lib.site-packages.libfuturize.fixes',
              'venv.Lib.site-packages.mpl_toolkits.mplot3d', 'venv.Lib.site-packages.mpl_toolkits.axes_grid',
              'venv.Lib.site-packages.mpl_toolkits.axes_grid1', 'venv.Lib.site-packages.mpl_toolkits.axisartist',
              'venv.Lib.site-packages.libpasteurize', 'venv.Lib.site-packages.libpasteurize.fixes',
              'venv.Lib.site-packages.pkg_resources', 'venv.Lib.site-packages.pkg_resources.extern',
              'venv.Lib.site-packages.pkg_resources._vendor', 'venv.Lib.site-packages.pkg_resources._vendor.packaging',
              'WorkingBuild'],
    url='',
    license='',
    author='The FriendorFoe Team',
    author_email='',
    description=''
)
