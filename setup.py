from setuptools import setup, find_packages

def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='yandex_music_api',
    version='1.0.4',
    author='LordCode',
    author_email='support@lordcord.fun',
    description='This is my first module',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://lordcord.fun',
    packages=find_packages(),
    install_requires=['aiohttp>=3.9.3', 'orjson>=3.9.15', 'xmltodict>=0.13.0'],
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='example python',
    project_urls={
        'Documentation': 'https://docs.lordcord.fun'
    },
    python_requires='>=3.7'
)
