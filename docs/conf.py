"""Sphinx configuration."""

from importlib import metadata

project = "remagic"
author = "Ificiana"
copyright = "Ificiana"
release = metadata.version("remagic")

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "myst_parser",
]

autosummary_generate = True
autodoc_member_order = "bysource"
autodoc_typehints = "none"
typehints_defaults = "comma"
napoleon_google_docstring = True
nitpicky = True
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

html_theme = "furo"
html_title = f"remagic {release}"
html_theme_options = {
    "source_repository": "https://github.com/ificiana/remagic",
    "source_branch": "main",
    "source_directory": "docs/",
}
