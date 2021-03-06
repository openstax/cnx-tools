import os.path as path
from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))
version = {}
with open(path.join(here, 'contentcopytool', '__version__.py')) as f:
  exec(f.read(), version)

setup(
  name = 'content-copy-tool',
  version = version['__version__'],
  description = 'Openstax Content Copy Tool',
  author = 'westonnovelli',
  maintainer = 'therealmarv, tomjw64',
  python_requires = '>=2.7.0,<3',
  url = 'https://github.com/openstax/cnx-tools',
  packages = find_packages(),
  install_requires = [
    'requests',
    'requests[security]',
    'pyOpenSSL',
    'ndg-httpsclient',
    'pyasn1'
  ],
  entry_points = {
    'console_scripts': [
      'content-copy=contentcopytool.content_copy:main',
    ],
  },
)
