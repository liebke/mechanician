from setuptools import setup, find_packages

setup(
    name='dandyhare',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'openai',
        'rich',
        'python-dotenv',

    ],
    entry_points={
        'console_scripts': [
            'dandyhare=dandyhare.main:main',
        ],
    },
    author='David Edgar Liebke',
    author_email='david@liebke.ai',
    description='<Your-Project-Description>',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/liebke/dandyhare',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)