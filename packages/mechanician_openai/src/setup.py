from setuptools import setup, find_packages

setup(
    name='mechanician_openai',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'mechanician>=0.1.0',
        'openai>=1.11.0,<2.0.0',
    ],
    author='David Edgar Liebke',
    author_email='david@liebke.ai',
    description='OpenAI enabled Daring Mechanician Library.',
    long_description=open('../README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/liebke/mechanician',
)