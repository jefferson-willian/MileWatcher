from setuptools import setup, find_packages

setup(
    name='milewatcher',
    version='0.1.0',
    description='TBD',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jefferson-willian/MileWatcher',
    packages=find_packages(where='.'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Utilities',
    ],
    python_requires='>=3.9',
    install_requires=[
        'requests',
        'beautifulsoup4',
    ],
)
