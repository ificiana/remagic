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

html_theme = "shibuya"
html_title = f"remagic {release}"
html_static_path = ["_static"]
html_logo = "_static/logo.svg"
html_favicon = "_static/favicon.svg"
html_theme_options = {
    "github_url": "https://github.com/ificiana/remagic",
}
