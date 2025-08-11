"""Sphinx configuration for Moderately AI Python SDK."""

import os
import sys

# Add the src directory to the path so we can import the package
sys.path.insert(0, os.path.abspath("../src"))

# Import the package to get version
import moderatelyai_sdk

# Project information
project = "Moderately AI Python SDK"
copyright = "2025, Moderately AI"
author = "Moderately AI"
release = moderatelyai_sdk.__version__
version = ".".join(release.split(".")[:2])  # Short X.Y version

# General configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx_autodoc_typehints",
    "myst_parser",
]

# Source file parsers
source_suffix = {
    ".rst": None,
    ".md": None,
}

# Master document
master_doc = "index"

# Language and locale
language = "en"

# Exclude patterns
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

# Autodoc configuration
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__,__dict__,__module__",
    "show-inheritance": True,
}

# Automatically generate stub pages for API documentation
autosummary_generate = True
autosummary_imported_members = True

# Napoleon settings for Google/NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Type hints configuration
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"
always_document_param_types = True

# Intersphinx mapping for cross-references
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "httpx": ("https://www.python-httpx.org/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

# Todo extension
todo_include_todos = True

# HTML theme options
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "canonical_url": "",
    "analytics_id": "",
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "vcs_pageview_mode": "",
    "style_nav_header_background": "#2980B9",
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

html_context = {
    "display_github": True,
    "github_user": "moderately-ai",
    "github_repo": "platform-sdk",
    "github_version": "main",
    "conf_py_path": "/python/docs/",
}

html_static_path = ["_static"]
html_css_files = []

# Custom sidebar templates
html_sidebars = {
    "**": [
        "relations.html",  # needs 'show_related': True theme option to display
        "searchbox.html",
    ]
}

# Output file base name for HTML help builder
htmlhelp_basename = "ModeratelyAIPythonSDKdoc"

# LaTeX output configuration
latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    "papersize": "letterpaper",
    # The font size ('10pt', '11pt' or '12pt').
    "pointsize": "10pt",
    # Additional stuff for the LaTeX preamble.
    "preamble": "",
    # Latex figure (float) alignment
    "figure_align": "htbp",
}

# Grouping the document tree into LaTeX files
latex_documents = [
    (
        master_doc,
        "ModeratelyAIPythonSDK.tex",
        "Moderately AI Python SDK Documentation",
        "Moderately AI",
        "manual",
    ),
]

# Manual page output configuration
man_pages = [
    (
        master_doc,
        "moderatelyaipythonsdk",
        "Moderately AI Python SDK Documentation",
        [author],
        1,
    )
]

# Texinfo output configuration
texinfo_documents = [
    (
        master_doc,
        "ModeratelyAIPythonSDK",
        "Moderately AI Python SDK Documentation",
        author,
        "ModeratelyAIPythonSDK",
        "Python SDK for Moderately AI platform",
        "Miscellaneous",
    ),
]

# Epub output configuration
epub_title = project
epub_exclude_files = ["search.html"]

# MyST parser configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "tasklist",
]

# Add any custom CSS files
def setup(app):
    """Add custom CSS and JS files."""
    pass
