from setuptools import setup, find_packages

def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='yandex_music_api',
    version='0.0.2',
    author='LordCode',
    author_email='support@lordcord.fun',
    description='This is my first module',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://lordcord.fun',
    packages=find_packages(),
    install_requires=['requests>=2.25.1'],
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='example python',
    project_urls={
        'Documentation': 'link'
    },
    python_requires='>=3.7'
)
