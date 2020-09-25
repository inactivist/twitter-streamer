#!/usr/bin/env python

import re

from setuptools import find_packages, setup

VERSION_FILE = "streamer/__init__.py"
with open(VERSION_FILE) as version_file:
    match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.MULTILINE
    )

if match:
    version = match.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSION_FILE,))

with open("README.md") as readme_file:
    long_description = readme_file.read()

setup(
    name="twitter-streamer",
    version=version,
    description="Twitter streaming utility for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author="Michael Curry",
    author_email="thatmichaelcurry@gmail.com",
    url="https://github.com/inactivist/twitter-streamer",
    project_urls={
        "Documentation": "https://github.com/inactivist/twitter-streamer/blob/master/README.md",
        "Issue Tracker": "https://github.com/inactivist/twitter-streamer/issues",
        "Source Code": "https://github.com/inactivist/twitter-streamer",
    },
    packages=find_packages(),
    install_requires=["tweepy==3.9"],
    keywords="twitter utility",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    zip_safe=True,
    entry_points={"console_scripts": ["twitter-streamer=streamer.streamer:main"]},
)
