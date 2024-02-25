from setuptools import setup, find_packages

setup(
    name='mechanician-tmdb',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,  # Required to include files specified in MANIFEST.in
    install_requires=[
        'mechanician>=0.1.3',
        'mechanician_openai>=0.1.3',
        'python-dotenv>=0.17.1',
        'rich>=10.0.0',
        'requests>=2.26.0',
    ],
    author='David Edgar Liebke',
    author_email='david@gmail.com',
    description='An TMDb example application of the Daring Mechanician library.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/liebke/mechanician/tree/main/examples/tmdb',
)