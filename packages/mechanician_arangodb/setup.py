from setuptools import setup, find_packages

setup(
    name='mechanician_arangodb',
    version='0.1.2',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'mechanician>=0.1.2',
        'python-arango>=5.0.0',
    ],
    author='David Edgar Liebke',
    author_email='david@gmail.com',
    description='Daring Mechanician AITools for interacting with ArangoDB Graph Databases.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/liebke/mechanician',
)