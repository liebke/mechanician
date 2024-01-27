from setuptools import setup, find_packages

setup(
    name='dandyhare',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'rich',
        'python-dotenv',
    ],
    extras_require={
        'openai': [
            # List the dependencies for the dandyhare.openai package here
            'openai',
        ]
    },
    author='David Edgar Liebke',
    author_email='david@liebke.ai',
    description='<Your-Project-Description>',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/liebke/dandyhare',
)