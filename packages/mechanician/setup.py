from setuptools import setup, find_packages

setup(
    name='mechanician',
    version='0.1.2',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'rich>=10.0.0',
    ],
    author='David Edgar Liebke',
    author_email='david@gmail.com',
    description='Building tools that use AI by building tools that AIs use.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/liebke/mechanician',
)