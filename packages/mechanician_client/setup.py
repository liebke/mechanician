from setuptools import setup, find_packages

setup(
    name='mechanician-client',
    version='0.1.4',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'asyncio',
        'websockets',
        'requests',
        # for TTS
        # 'pyaudio',
        'openai',
        # must install portaudio separately: 
        # * MacOS: brew install portaudio
        # * Linux: sudo apt-get install portaudio19-dev
        # * Windows: download from http://www.portaudio.com/download.html

        # for STT
        'openai-whisper', 
        'sounddevice',
        # 'webrtcvad' # VOICE ADTIVATION DETECTION, NOT NEEDED
    ],
    author='David Edgar Liebke',
    author_email='david@gmail.com',
    description='Command line tools for working with Mechanician AI Studio.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/liebke/mechanician',
)
