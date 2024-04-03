from setuptools import setup, find_packages

setup(
    name='mechanician_studio_demo',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,  # Required to include files specified in MANIFEST.in
    install_requires=[
        'mechanician>=0.1.3',
        'mechanician-openai>=0.1.3',
        'mechanician-studio>=0.1.0',
        'mechanician-arangodb>=0.1.3',
        'mechanician-chroma>=0.1.4',
        'python-dotenv>=0.17.1',
    ],
    author='David Edgar Liebke',
    author_email='david@gmail.com',
    description='Daring Mechanician AI Studio Demo.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/liebke/mechanician',
)