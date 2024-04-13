from setuptools import setup, find_packages

setup(
    name='mechanician_studio',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,  # This line includes non-Python files
    install_requires=[
        'mechanician>=0.1.3',
        'fastapi>=0.110.0',
        'uvicorn[standard]>=0.13.4',
        'jinja2>=2.11.3',
        'python-jose[cryptography]',
        'passlib[bcrypt]',
        # 'python-multipart',
        'aiofiles'
    ],
    author='David Edgar Liebke',
    author_email='david@gmail.com',
    description='Daring Mechanician FastAPI-based Web UI.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/liebke/mechanician',
)
