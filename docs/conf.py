from datetime import date

# METADATA

project = "PowerCLI"
copyright = f"{date.today().year}, Jonas da Silva"
author = "Jonas da Silva"


# GENERAL CONFIG

extensions = ["autodoc2", "myst_parser", "sphinx_inline_tabs", "sphinx.ext.intersphinx"]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# HTML CONFIG

html_theme = "furo"
html_theme_options = {
    "source_repository": "https://github.com/phoenixr-codes/powercli/",
    "source_branch": "stable",
    "source_directory": "docs/",
}
html_logo = "../assets/logo.svg"
html_favicon = "../assets/icon.svg"
html_static_path = ["_static"]


# EXTENSIONS CONFIG

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

autodoc2_output_dir = "api"
autodoc2_packages = ["../powercli"]
autodoc2_render_plugin = "myst"
autodoc2_hidden_objects = {"dunder", "private", "inherited"}

# autodoc2_module_all_regexes = [r"powercli\.\w.*"]
# This is required to only include objects specified in `__all__`. The `powercli\.\w` prefix is required
# to prevent this behavior for `__init__.py` or else only `__init__.py` would be documented.

autodoc2_index_template = """API Reference
=============

This page contains auto-generated API reference documentation.

.. toctree::
   :titlesonly:
{% for package in top_level %}
   {{ package }}
{%- endfor %}"""
# Here, we essentially dirtily remove the mention to `sphinx-autodoc2`.

myst_enable_extensions = {"colon_fence", "smartquotes"}
