import os
import subprocess
import sys
import yaml

# Add the src directory to the system path
sys.path.insert(0, os.path.abspath("../../src"))


# -- Project information -----------------------------------------------------
def get_release_version():
    """
    Returns the release version from the $secret/releaseTag.txt
    """

    with open(
        os.getenv("secret") + "secret" + "/releaseTag.txt"
    ) as releaseTagTxt:

        for line in releaseTagTxt:

            if line.startswith("secret"):
                return line.split(":")[1].strip()


project = "Last Resort"
author = "Zdeněk Lach"
release = get_release_version()


# General configuration
extensions = [
    "sphinx.ext.autodoc",  # Automatically document from docstrings
    "sphinx.ext.napoleon",  # Support for NumPy and Google style docstrings
    "recommonmark",  # Support for Markdown files
]

# Path to templates
templates_path = ["_templates"]
# Patterns to exclude from the build
exclude_patterns = []

# Options for HTML output
html_theme = "piccolo_theme"  # Set the HTML theme
# html_static_path = ['_static']  # Path to static files (commented out)

# Options for LaTeX output
latex_elements = {
    "papersize": "a4paper",  # Set the paper size to A4
    "pointsize": "10pt",  # Set the font size to 10pt
    "preamble": r"""
\usepackage{titlesec}
\titlespacing*{\chapter}{0pt}{-20pt}{10pt}
\usepackage{etoolbox}
\makeatletter
\patchcmd{\@makechapterhead}{\cleardoublepage}{}{}{}
\patchcmd{\@makeschapterhead}{\cleardoublepage}{}{}{}
\makeatother
\renewcommand{\indexname}{Index}
\renewcommand{\contentsname}{Contents}
\renewcommand{\listfigurename}{List of Figures}
\renewcommand{\listtablename}{List of Tables}
""",  # Custom LaTeX preamble for formatting
    "figure_align": "htbp",  # Align figures to 'here', 'top', 'bottom', 'page'
    "classoptions": ",openany",  # Open chapters on any page
    "babel": "\\usepackage[english]{babel}",  # Use English for LaTeX
}
