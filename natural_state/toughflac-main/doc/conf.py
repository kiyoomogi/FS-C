# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("../"))


# -- Project information -----------------------------------------------------
import toughflac

project = "toughflac"
copyright = "2022, Keurfon Luu"
author = "Keurfon Luu"

version = toughflac.__version__
release = version


# -- General configuration ---------------------------------------------------

master_doc = "index"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
# pip install sphinxcontrib-bibtex
# pip install sphinx-rtd-theme
# pip install git+https://github.com/Naeka/pybtex-apa-style
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx.ext.napoleon",
    "sphinxcontrib.bibtex",
]

# Napoleon settings
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
# napoleon_use_admonition_for_examples = False
# napoleon_use_admonition_for_notes = False
# napoleon_use_admonition_for_references = False
# napoleon_use_ivar = True
# napoleon_use_param = True
# napoleon_use_rtype = True

# BibTeX
bibtex_bibfiles = ["bib/library.bib"]

# Numfig settings
numfig = True
numfig_format = {
    "figure": "Figure %s",
}

# Add any paths that contain templates here, relative to this directory.
templates_path = [
    "_templates",
]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"
html_theme_path = [
    "_themes",
]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = [
#     "_static",
# ]


# -- Options for LaTeX output  ---------------------------------------------------

latex_engine = "pdflatex"
latex_elements = {
    "papersize": "a4paper",
    "releasename": "Version",
    "fncychap": "\\usepackage{fncychap}",
    "figure_align": "htbp",
    "pointsize": "10pt",
    "preamble": r"""
        \addto\captionsenglish{\renewcommand{\contentsname}{Contents}}

        \def\topfraction{0.9} % 90 percent of the page may be used by floats on top
        \def\bottomfraction{0.9} % the same at the bottom
        \def\textfraction{0.01} % at least 1 percent must be reserved for text
        \def\tightlist{}

        \usepackage{sansmathfonts}
        \usepackage{helvet}
        \renewcommand{\familydefault}{\sfdefault}
    """,
    # "maketitle": "\\maketitle",
    "tableofcontents": "\\tableofcontents",
    "sphinxsetup": "verbatimwithframe=false, VerbatimColor={rgb}{0.97,0.97,0.97}",
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "main.tex", "TOUGH3-FLAC for Dummies", "Keurfon Luu", "manual",)
]

latex_additional_files = [
    "tfreport.sty",
]
