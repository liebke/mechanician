from setuptools import setup, find_packages

setup(
    name='mechanician_chroma',
    version='0.1.4',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'mechanician>=0.1.3',
        'chromadb>=0.1.0',
        'beautifulsoup4>=4.9.3',
        'requests>=2.25.1',
        'sentence_transformers>=2.0.0',
        'langchain>=0.1.0',
        'PyPDF2>=1.26.0',
    ],
    author='David Edgar Liebke',
    author_email='david@gmail.com',
    description='Daring Mechanician ResourceConnector for interacting with Chroma Embeddings Databases.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/liebke/mechanician',
)
