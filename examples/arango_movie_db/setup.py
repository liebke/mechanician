from setuptools import setup, find_packages

setup(
    name='arango_movie_db',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'mechanician>=0.1.0',
        'mechanician-openai>=0.1.0',
        'mechanician-arangodb>=0.1.0',
        'python-arango>=5.0.0',
        'python-dotenv>=0.17.1',
    ],
    author='David Edgar Liebke',
    author_email='david@liebke.ai',
    description='Daring Mechanician ArangoDB Movie Database example.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/liebke/mechanician',
)