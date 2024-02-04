from setuptools import setup, find_packages

setup(
    name='mechanician_openai',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'mechanician_core',
        'openai',
        'rich',
        'python-dotenv',
    ],
    author='David Edgar Liebke',
    author_email='david@liebke.ai',
    description='OpenAI enabled Daring Mechanician Library.',
    long_description=open('../README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/liebke/mechanician',
)