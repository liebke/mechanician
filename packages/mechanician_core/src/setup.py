from setuptools import setup, find_packages

setup(
    name='mechanician_core',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'rich',
        'python-dotenv',
    ],
    author='David Edgar Liebke',
    author_email='david@liebke.ai',
    description='Building tools that use AI and building tools that AIs use.',
    long_description=open('../README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/liebke/mechanician',
)