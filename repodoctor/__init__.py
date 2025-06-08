"""
RepoDoctor - Automated technical documentation generator for code repositories

RepoDoctor analyzes code repositories and generates comprehensive technical documentation
using Large Language Model (LLM) analysis through OpenRouter API.

Features:
- Multi-language code analysis (Python, JavaScript, TypeScript, Java, C/C++, Rust, Go)
- Automatic dependency extraction and visualization
- Structured markdown documentation generation
- Optional Docusaurus site generation
- Professional CLI interface with parallel processing
"""

__version__ = "0.0.1"
__author__ = "Alexander Orlov"
__email__ = "pipy@orlov.ai"
__license__ = "MIT"

from .generator import DocumentationGenerator
from .analyzer import FileAnalyzer
from .client import OpenRouterClient

__all__ = [
    "DocumentationGenerator",
    "FileAnalyzer", 
    "OpenRouterClient",
    "__version__"
]
