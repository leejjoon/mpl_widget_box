# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mpl_widget_box', 'mpl_widget_box.misc']

package_data = \
{'': ['*']}

install_requires = \
['fontawesomefree>=6.1', 'matplotlib>=3,<3.6']

setup_kwargs = {
    'name': 'mpl-widget-box',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Jae-Joon Lee',
    'author_email': 'lee.j.joon@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'classifiers': ['Framework :: Matplotlib'],
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)

