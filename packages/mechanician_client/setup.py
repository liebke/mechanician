from setuptools import setup, find_packages

setup(
    name='mechanician-client',
    version='0.1.4',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'asyncio',
        'websockets',
        'requests',
    ],
    author='David Edgar Liebke',
    author_email='david@gmail.com',
    description='Command line tools for working with Mechanician AI Studio.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/liebke/mechanician',
)
