from setuptools import setup, find_packages

setup(
    name='html-extractor',
    version='0.1.0',
    author='Victor Delaplaine',
    author_email='auth.sentry@egmail.com.com',
    description='A library to extract login-related HTML elements from web pages.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/ByVictorrr/LoginHarvest",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'beautifulsoup4',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)