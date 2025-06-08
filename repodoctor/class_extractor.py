import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, NamedTuple
import logging

logger = logging.getLogger(__name__)

class ClassInfo(NamedTuple):
    """Information about a class"""
    name: str
    parent_classes: List[str]
    methods: List[str]
    properties: List[str]
    file_path: str
    line_number: int

class ClassExtractor:
    """Extract class hierarchy information from code files"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.classes_by_file = {}
        self.all_classes = {}
    
    def extract_classes_from_files(self, files: List[str]) -> Dict[str, List[ClassInfo]]:
        """Extract class information from all files"""
        for file_path in files:
            full_path = self.repo_path / file_path
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Determine file type
                file_type = self._get_file_type(file_path)
                
                if file_type == 'python':
                    classes = self._extract_python_classes(content, file_path)
                elif file_type in ['javascript', 'typescript']:
                    classes = self._extract_js_classes(content, file_path)
                elif file_type == 'java':
                    classes = self._extract_java_classes(content, file_path)
                elif file_type == 'php':
                    classes = self._extract_php_classes(content, file_path)
                else:
                    classes = []
                
                if classes:
                    self.classes_by_file[file_path] = classes
                    # Store all classes with their full names
                    for cls in classes:
                        self.all_classes[cls.name] = cls
                
            except Exception as e:
                logger.warning(f"Could not extract classes from {file_path}: {e}")
        
        return self.classes_by_file
    
    def get_class_hierarchy(self) -> Dict[str, List[str]]:
        """Get inheritance hierarchy for all classes"""
        hierarchy = {}
        
        for class_name, class_info in self.all_classes.items():
            hierarchy[class_name] = class_info.parent_classes
        
        return hierarchy
    
    def _get_file_type(self, file_path: str) -> str:
        """Get file type based on extension"""
        extension = Path(file_path).suffix.lower()
        type_mapping = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.php': 'php'
        }
        return type_mapping.get(extension, 'unknown')
    
    def _extract_python_classes(self, content: str, file_path: str) -> List[ClassInfo]:
        """Extract Python classes using AST"""
        classes = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Extract parent classes
                    parent_classes = []
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            parent_classes.append(base.id)
                        elif isinstance(base, ast.Attribute):
                            # Handle cases like module.ClassName
                            parent_classes.append(ast.unparse(base))
                    
                    # Extract methods
                    methods = []
                    properties = []
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append(item.name)
                        elif isinstance(item, ast.Assign):
                            # Class variables/properties
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    properties.append(target.id)
                    
                    class_info = ClassInfo(
                        name=node.name,
                        parent_classes=parent_classes,
                        methods=methods,
                        properties=properties,
                        file_path=file_path,
                        line_number=node.lineno
                    )
                    classes.append(class_info)
        
        except SyntaxError as e:
            logger.warning(f"Could not parse Python file {file_path}: {e}")
            # Fallback to regex-based extraction
            classes.extend(self._extract_python_classes_regex(content, file_path))
        
        return classes
    
    def _extract_python_classes_regex(self, content: str, file_path: str) -> List[ClassInfo]:
        """Fallback regex-based Python class extraction"""
        classes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            # Match class definitions
            match = re.match(r'^class\s+(\w+)(?:\(([^)]+)\))?:', line)
            if match:
                class_name = match.group(1)
                parents_str = match.group(2) or ""
                
                # Parse parent classes
                parent_classes = []
                if parents_str:
                    parents = [p.strip() for p in parents_str.split(',')]
                    parent_classes = [p for p in parents if p and not p.startswith('object')]
                
                # Extract methods (simple approach)
                methods = []
                for j in range(i + 1, min(i + 50, len(lines))):  # Look ahead 50 lines
                    method_line = lines[j].strip()
                    if method_line.startswith('def '):
                        method_match = re.match(r'def\s+(\w+)', method_line)
                        if method_match:
                            methods.append(method_match.group(1))
                    elif method_line.startswith('class '):
                        break  # Found another class
                
                class_info = ClassInfo(
                    name=class_name,
                    parent_classes=parent_classes,
                    methods=methods,
                    properties=[],  # Hard to extract with regex
                    file_path=file_path,
                    line_number=i + 1
                )
                classes.append(class_info)
        
        return classes
    
    def _extract_js_classes(self, content: str, file_path: str) -> List[ClassInfo]:
        """Extract JavaScript/TypeScript classes using regex"""
        classes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Match class definitions: class ClassName extends ParentClass
            match = re.match(r'^class\s+(\w+)(?:\s+extends\s+(\w+))?', line)
            if match:
                class_name = match.group(1)
                parent_class = match.group(2)
                
                parent_classes = [parent_class] if parent_class else []
                
                # Extract methods
                methods = []
                for j in range(i + 1, min(i + 100, len(lines))):
                    method_line = lines[j].strip()
                    
                    # Match method definitions
                    method_match = re.match(r'^(\w+)\s*\(', method_line)
                    if method_match and not method_line.startswith('//'):
                        method_name = method_match.group(1)
                        # Skip common keywords
                        if method_name not in ['if', 'for', 'while', 'switch', 'return']:
                            methods.append(method_name)
                    elif method_line.startswith('class '):
                        break  # Found another class
                
                class_info = ClassInfo(
                    name=class_name,
                    parent_classes=parent_classes,
                    methods=methods,
                    properties=[],
                    file_path=file_path,
                    line_number=i + 1
                )
                classes.append(class_info)
        
        return classes
    
    def _extract_java_classes(self, content: str, file_path: str) -> List[ClassInfo]:
        """Extract Java classes using regex"""
        classes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Match class definitions
            class_match = re.match(r'^(?:public\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?', line)
            if class_match:
                class_name = class_match.group(1)
                parent_class = class_match.group(2)
                interfaces = class_match.group(3)
                
                parent_classes = []
                if parent_class:
                    parent_classes.append(parent_class)
                if interfaces:
                    # Parse implemented interfaces
                    interface_list = [i.strip() for i in interfaces.split(',')]
                    parent_classes.extend(interface_list)
                
                # Extract methods
                methods = []
                for j in range(i + 1, min(i + 100, len(lines))):
                    method_line = lines[j].strip()
                    
                    # Match method definitions
                    method_match = re.match(r'^(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?\w+\s+(\w+)\s*\(', method_line)
                    if method_match:
                        methods.append(method_match.group(1))
                    elif method_line.startswith('class ') or method_line.startswith('interface '):
                        break  # Found another class/interface
                
                class_info = ClassInfo(
                    name=class_name,
                    parent_classes=parent_classes,
                    methods=methods,
                    properties=[],
                    file_path=file_path,
                    line_number=i + 1
                )
                classes.append(class_info)
        
        return classes
    
    def _extract_php_classes(self, content: str, file_path: str) -> List[ClassInfo]:
        """Extract PHP classes using regex"""
        classes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Match class definitions
            class_match = re.match(r'^(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?', line)
            if class_match:
                class_name = class_match.group(1)
                parent_class = class_match.group(2)
                interfaces = class_match.group(3)
                
                parent_classes = []
                if parent_class:
                    parent_classes.append(parent_class)
                if interfaces:
                    interface_list = [i.strip() for i in interfaces.split(',')]
                    parent_classes.extend(interface_list)
                
                # Extract methods
                methods = []
                properties = []
                
                for j in range(i + 1, min(i + 100, len(lines))):
                    method_line = lines[j].strip()
                    
                    # Match method definitions
                    method_match = re.match(r'^(?:public|private|protected)?\s*function\s+(\w+)\s*\(', method_line)
                    if method_match:
                        methods.append(method_match.group(1))
                    
                    # Match properties
                    prop_match = re.match(r'^(?:public|private|protected)?\s*\$(\w+)', method_line)
                    if prop_match:
                        properties.append(prop_match.group(1))
                    
                    elif method_line.startswith('class '):
                        break  # Found another class
                
                class_info = ClassInfo(
                    name=class_name,
                    parent_classes=parent_classes,
                    methods=methods,
                    properties=properties,
                    file_path=file_path,
                    line_number=i + 1
                )
                classes.append(class_info)
        
        return classes
