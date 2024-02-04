from setuptools import setup, find_packages

setup(
    name='mechanician_arangodb',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'mechanician_core',
        'python-arango',
        'rich',
        'python-dotenv',
    ],
    extras_require={
        'mechanician_openai': [
            # List the dependencies for the mechanician.openai package here
            'openai',
        ]
    },
    author='David Edgar Liebke',
    author_email='david@liebke.ai',
    description='Daring Mechanician ArangoDB Graph Database library.',
    long_description=open('../README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/liebke/mechanician',
)