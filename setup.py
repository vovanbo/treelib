from setuptools import setup
from ttree import __version__

setup(
    name="ttree",
    version=__version__,
    url='https://github.com/vovanbo/ttree',
    author='Vladimir Bolshakov',
    author_email='vovanbo@gmail.com',
    description='Taxonomy tree data structure implementation.',
    long_description='This is a taxonomy tree data structure implementation '
                     'in Python.',
    license="Apache License, Version 2.0",
    packages=['ttree'],
    keywords=['data structure', 'tree', 'tools', 'taxonomy'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: Freely Distributable',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
