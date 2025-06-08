import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Set, Optional
import logging

logger = logging.getLogger(__name__)

class FileAnalyzer:
    """Analyze code files to extract imports, dependencies, and determine file types"""
    
    # Supported file extensions and their types
    SUPPORTED_EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript', 
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.hpp': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.rs': 'rust',
        '.go': 'go',
        '.php': 'php',
        '.toml': 'toml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.json': 'json',
        '.md': 'markdown',
        '.txt': 'text'
    }
    
    # Files/directories to ignore
    IGNORE_PATTERNS = {
        '__pycache__',
        '.git',
        '.venv',
        'venv',
        'node_modules',
        '.pytest_cache',
        'dist',
        'build',
        '.DS_Store',
        '*.pyc',
        '*.pyo',
        '*.egg-info',
        '*-docusaurus',
        '.docusaurus'
    }
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        
    def scan_code_files(self) -> List[str]:
        """Scan repository for code files to document"""
        code_files = []
        
        for root, dirs, files in os.walk(self.repo_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore(d)]
            
            for file in files:
                if self._should_ignore(file):
                    continue
                    
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.repo_path)
                
                if self.should_document(str(relative_path)):
                    code_files.append(str(relative_path))
        
        logger.info(f"Found {len(code_files)} files to document")
        return sorted(code_files)
    
    def should_document(self, file_path: str) -> bool:
        """Check if file should be documented"""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        # Check if extension is supported
        if extension not in self.SUPPORTED_EXTENSIONS:
            return False
            
        # Don't document test files unless they're important
        if 'test' in path.name.lower() and extension in ['.py', '.js', '.ts']:
            return True  # Include test files for now
            
        return True
    
    def get_file_type(self, file_path: str) -> str:
        """Get file type based on extension"""
        extension = Path(file_path).suffix.lower()
        return self.SUPPORTED_EXTENSIONS.get(extension, 'text')
    
    def extract_dependencies(self, content: str, file_path: str) -> List[str]:
        """Extract imports/dependencies from file content"""
        file_type = self.get_file_type(file_path)
        
        if file_type == 'python':
            return self._extract_python_imports(content)
        elif file_type in ['javascript', 'typescript']:
            return self._extract_js_imports(content)
        elif file_type == 'java':
            return self._extract_java_imports(content)
        elif file_type in ['c', 'cpp']:
            return self._extract_c_imports(content)
        elif file_type == 'rust':
            return self._extract_rust_imports(content)
        elif file_type == 'go':
            return self._extract_go_imports(content)
        elif file_type == 'php':
            return self._extract_php_imports(content)
        else:
            return []
    
    def analyze_project_dependencies(self, files: List[str]) -> Dict[str, List[str]]:
        """Analyze dependencies across all project files"""
        dependency_graph = {}
        
        for file_path in files:
            full_path = self.repo_path / file_path
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                deps = self.extract_dependencies(content, file_path)
                dependency_graph[file_path] = deps
                
            except Exception as e:
                logger.warning(f"Could not analyze dependencies for {file_path}: {e}")
                dependency_graph[file_path] = []
        
        return dependency_graph
    
    def _should_ignore(self, name: str) -> bool:
        """Check if file/directory should be ignored"""
        # Check for docs folders with UUID pattern
        if re.match(r'.*-docs-[a-f0-9]{8}$', name):
            return True
            
        for pattern in self.IGNORE_PATTERNS:
            if pattern.startswith('*'):
                if name.endswith(pattern[1:]):
                    return True
            elif name == pattern or name.startswith(pattern):
                return True
        return False
    
    def _extract_python_imports(self, content: str) -> List[str]:
        """Extract Python imports using AST parsing"""
        imports = []
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        
        except SyntaxError:
            # Fallback to regex if AST parsing fails
            imports.extend(self._extract_python_imports_regex(content))
        
        return list(set(imports))  # Remove duplicates
    
    def _extract_python_imports_regex(self, content: str) -> List[str]:
        """Fallback regex-based Python import extraction"""
        imports = []
        
        # Match "import module" and "from module import ..."
        import_patterns = [
            r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
            r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import'
        ]
        
        for line in content.split('\n'):
            line = line.strip()
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    imports.append(match.group(1))
        
        return imports
    
    def _extract_php_imports(self, content: str) -> List[str]:
        """Extract PHP use statements, requires, and includes"""
        imports = []
        
        # Patterns for different PHP import styles
        patterns = [
            r'^use\s+([a-zA-Z_\\][a-zA-Z0-9_\\]*)',  # use statements
            r'require(?:_once)?\s*\(?[\'"]([^\'"]+)[\'"]',  # require/require_once
            r'include(?:_once)?\s*\(?[\'"]([^\'"]+)[\'"]',  # include/include_once
        ]
        
        for line in content.split('\n'):
            line = line.strip()
            for pattern in patterns:
                matches = re.findall(pattern, line)
                imports.extend(matches)
        
        return list(set(imports))
    
    def _extract_js_imports(self, content: str) -> List[str]:
        """Extract JavaScript/TypeScript imports"""
        imports = []
        
        # Patterns for different import styles
        patterns = [
            r'^import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',  # import ... from 'module'
            r'^import\s+[\'"]([^\'"]+)[\'"]',                # import 'module'
            r'require\([\'"]([^\'"]+)[\'"]\)',              # require('module')
        ]
        
        for line in content.split('\n'):
            line = line.strip()
            for pattern in patterns:
                matches = re.findall(pattern, line)
                imports.extend(matches)
        
        return list(set(imports))
    
    def _extract_java_imports(self, content: str) -> List[str]:
        """Extract Java imports"""
        imports = []
        
        pattern = r'^import\s+(?:static\s+)?([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
        
        for line in content.split('\n'):
            line = line.strip()
            match = re.match(pattern, line)
            if match:
                imports.append(match.group(1))
        
        return imports
    
    def _extract_c_imports(self, content: str) -> List[str]:
        """Extract C/C++ includes"""
        imports = []
        
        pattern = r'#include\s*[<"]([^>"]+)[>"]'
        
        for line in content.split('\n'):
            line = line.strip()
            match = re.match(pattern, line)
            if match:
                imports.append(match.group(1))
        
        return imports
    
    def _extract_rust_imports(self, content: str) -> List[str]:
        """Extract Rust use statements"""
        imports = []
        
        pattern = r'^use\s+([a-zA-Z_][a-zA-Z0-9_]*(?:::[a-zA-Z_][a-zA-Z0-9_]*)*)'
        
        for line in content.split('\n'):
            line = line.strip()
            match = re.match(pattern, line)
            if match:
                imports.append(match.group(1))
        
        return imports
    
    def _extract_go_imports(self, content: str) -> List[str]:
        """Extract Go imports"""
        imports = []
        in_import_block = False
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line.startswith('import ('):
                in_import_block = True
                continue
            elif line == ')' and in_import_block:
                in_import_block = False
                continue
            elif in_import_block:
                # Extract quoted import path
                match = re.search(r'"([^"]+)"', line)
                if match:
                    imports.append(match.group(1))
            elif line.startswith('import '):
                # Single import
                match = re.search(r'"([^"]+)"', line)
                if match:
                    imports.append(match.group(1))
        
        return imports
