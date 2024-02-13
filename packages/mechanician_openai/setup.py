from setuptools import setup, find_packages

setup(
    name='mechanician_openai',
    version='0.1.2',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'mechanician>=0.1.2',
        'openai>=1.11.0,<2.0.0',
    ],
    author='David Edgar Liebke',
    author_email='david@gmail.com',
    description='Daring Mechanician AIConnectors for OpenAI Chat and Assistants APIs.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/liebke/mechanician',
)
