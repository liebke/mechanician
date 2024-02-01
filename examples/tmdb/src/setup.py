from setuptools import setup, find_packages

setup(
    name='mechanician-tmdb',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'mechanician',
        'openai',
        'python-dotenv',
        'rich'
    ],
    author='David Edgar Liebke',
    author_email='david@liebke.ai',
    description='An example application of the Daring Mechanician library.',
    long_description=open('../README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/liebke/mechanician/tree/main/examples/tmdb',
)