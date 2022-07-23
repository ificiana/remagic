"""This module contains setup instructions for remagic."""
import codecs
import os

import setuptools

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

setuptools.setup(
    name="remagic",
    version="0.0.4",
    author="Ificiana",
    author_email="ificiana@gmail.com",
    packages=["remagic"],
    package_data={"": ["LICENSE"], "remagic": ["py.typed", "main.pyi"]},
    url="https://github.com/ificiana/remagic",
    license="MIT License",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    description=(
        "Work with RegEx with relative ease."
        " Partly inspired by magic-regexp for Node"
    ),
    include_package_data=True,
    long_description_content_type="text/markdown",
    long_description=long_description,
    keywords=["remagic", "regex"],
)
