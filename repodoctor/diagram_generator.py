from typing import Dict, List, Set, Optional
from pathlib import Path
import logging
from .class_extractor import ClassInfo

logger = logging.getLogger(__name__)

class MermaidDiagramGenerator:
    """Generate Mermaid diagrams for class hierarchies and dependencies"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
    
    def generate_class_diagram(self, classes_by_file: Dict[str, List[ClassInfo]], 
                             all_classes: Dict[str, ClassInfo]) -> str:
        """Generate Mermaid class diagram"""
        
        if not all_classes:
            return self._generate_empty_class_diagram()
        
        diagram_lines = ["```mermaid", "classDiagram"]
        
        # Add class definitions
        for class_name, class_info in all_classes.items():
            diagram_lines.append(f"    class {class_name} {{")
            
            # Add properties
            for prop in class_info.properties:
                # Use + for public, - for private (simplified)
                visibility = "+" if not prop.startswith("_") else "-"
                diagram_lines.append(f"        {visibility}{prop}")
            
            # Add methods
            for method in class_info.methods:
                # Use + for public, - for private (simplified)
                visibility = "+" if not method.startswith("_") else "-"
                diagram_lines.append(f"        {visibility}{method}()")
            
            diagram_lines.append("    }")
            diagram_lines.append("")
        
        # Add inheritance relationships
        for class_name, class_info in all_classes.items():
            for parent in class_info.parent_classes:
                # Check if parent class exists in our project
                if parent in all_classes:
                    diagram_lines.append(f"    {parent} <|-- {class_name}")
                else:
                    # External parent class - show as note
                    diagram_lines.append(f"    {class_name} : extends {parent}")
        
        # Add file location notes
        diagram_lines.append("")
        for class_name, class_info in all_classes.items():
            file_note = class_info.file_path.replace('\\', '/').replace('.py', '').replace('/', '.')
            diagram_lines.append(f"    {class_name} : <<{file_note}>>")
        
        diagram_lines.append("```")
        
        return "\n".join(diagram_lines)
    
    def generate_dependency_graph(self, dependency_graph: Dict[str, List[str]], 
                                project_files: Set[str]) -> str:
        """Generate Mermaid dependency graph"""
        
        if not dependency_graph:
            return self._generate_empty_dependency_graph()
        
        diagram_lines = ["```mermaid", "graph TD"]
        
        # Create nodes for project files
        file_nodes = {}
        node_counter = 0
        
        for file_path in sorted(project_files):
            node_id = f"F{node_counter}"
            file_nodes[file_path] = node_id
            
            # Create readable file name
            file_name = Path(file_path).name
            if len(file_name) > 20:
                file_name = file_name[:17] + "..."
            
            diagram_lines.append(f"    {node_id}[{file_name}]")
            node_counter += 1
        
        # Add external dependencies as separate nodes
        external_deps = set()
        for deps in dependency_graph.values():
            for dep in deps:
                if dep not in project_files and not self._is_standard_library(dep):
                    external_deps.add(dep)
        
        for dep in sorted(external_deps):
            node_id = f"E{node_counter}"
            file_nodes[dep] = node_id
            
            # Shorten long dependency names
            dep_name = dep
            if len(dep_name) > 15:
                dep_name = dep_name[:12] + "..."
            
            diagram_lines.append(f"    {node_id}[{dep_name}]")
            diagram_lines.append(f"    {node_id}:::external")
            node_counter += 1
        
        diagram_lines.append("")
        
        # Add dependencies as edges
        for file_path, deps in dependency_graph.items():
            if file_path in file_nodes:
                source_node = file_nodes[file_path]
                
                for dep in deps:
                    if dep in file_nodes:
                        target_node = file_nodes[dep]
                        diagram_lines.append(f"    {source_node} --> {target_node}")
        
        # Add styling
        diagram_lines.append("")
        diagram_lines.append("    classDef external fill:#f9f9f9,stroke:#999,stroke-width:2px")
        
        diagram_lines.append("```")
        
        return "\n".join(diagram_lines)
    
    def generate_file_structure_diagram(self, files: List[str]) -> str:
        """Generate a simple file structure diagram"""
        
        if not files:
            return "```mermaid\ngraph TD\n    A[No files found]\n```"
        
        diagram_lines = ["```mermaid", "graph TD"]
        
        # Group files by directory
        dirs = {}
        for file_path in files:
            path_parts = Path(file_path).parts
            
            if len(path_parts) == 1:
                # Root file
                if "root" not in dirs:
                    dirs["root"] = []
                dirs["root"].append(file_path)
            else:
                # File in directory
                dir_name = path_parts[0]
                if dir_name not in dirs:
                    dirs[dir_name] = []
                dirs[dir_name].append(file_path)
        
        node_counter = 0
        
        # Create directory nodes
        for dir_name in sorted(dirs.keys()):
            if dir_name == "root":
                continue
            
            dir_node = f"D{node_counter}"
            diagram_lines.append(f"    {dir_node}[{dir_name}/]")
            diagram_lines.append(f"    {dir_node}:::directory")
            
            # Add files in this directory
            for file_path in sorted(dirs[dir_name])[:5]:  # Limit to 5 files per directory
                file_node = f"F{node_counter}"
                file_name = Path(file_path).name
                diagram_lines.append(f"    {file_node}[{file_name}]")
                diagram_lines.append(f"    {dir_node} --> {file_node}")
                node_counter += 1
            
            if len(dirs[dir_name]) > 5:
                more_node = f"M{node_counter}"
                diagram_lines.append(f"    {more_node}[...{len(dirs[dir_name]) - 5} more files]")
                diagram_lines.append(f"    {more_node}:::more")
                diagram_lines.append(f"    {dir_node} --> {more_node}")
                node_counter += 1
            
            node_counter += 1
        
        # Add root files
        if "root" in dirs:
            for file_path in sorted(dirs["root"])[:3]:  # Limit root files
                file_node = f"R{node_counter}"
                file_name = Path(file_path).name
                diagram_lines.append(f"    {file_node}[{file_name}]")
                diagram_lines.append(f"    {file_node}:::root")
                node_counter += 1
        
        # Add styling
        diagram_lines.append("")
        diagram_lines.append("    classDef directory fill:#e1f5fe,stroke:#01579b,stroke-width:2px")
        diagram_lines.append("    classDef root fill:#f3e5f5,stroke:#4a148c,stroke-width:2px")
        diagram_lines.append("    classDef more fill:#fff3e0,stroke:#e65100,stroke-width:1px")
        
        diagram_lines.append("```")
        
        return "\n".join(diagram_lines)
    
    def _generate_empty_class_diagram(self) -> str:
        """Generate placeholder when no classes found"""
        return """```mermaid
classDiagram
    class NoClasses {
        +message: "No classes found in project"
        +suggestion: "Add classes to see hierarchy"
    }
    
    note for NoClasses "No class definitions were\nfound in the analyzed files"
```"""
    
    def _generate_empty_dependency_graph(self) -> str:
        """Generate placeholder when no dependencies found"""
        return """```mermaid
graph TD
    A[No Dependencies Found]
    A --> B[This usually means:]
    B --> C[No import statements]
    B --> D[Self-contained files]
    B --> E[Only standard library usage]
```"""
    
    def _is_standard_library(self, module_name: str) -> bool:
        """Check if module is part of standard library"""
        standard_libs = {
            # Python standard library (common modules)
            'os', 'sys', 'json', 'urllib', 'http', 'datetime', 'time',
            'collections', 'itertools', 'functools', 're', 'math',
            'random', 'pathlib', 'logging', 'threading', 'subprocess',
            'argparse', 'configparser', 'csv', 'xml', 'sqlite3',
            'ast', 'typing', 'dataclasses', 'enum', 'abc',
            
            # JavaScript/Node.js standard modules
            'fs', 'path', 'util', 'events', 'stream', 'crypto',
            'url', 'querystring', 'http', 'https', 'net',
            
            # Java standard library
            'java.lang', 'java.util', 'java.io', 'java.net',
            'java.text', 'java.time', 'java.math', 'java.security',
            
            # PHP standard library
            'stdClass', 'Exception', 'DateTime', 'PDO'
        }
        
        # Check if module starts with standard library name
        for std_lib in standard_libs:
            if module_name.startswith(std_lib):
                return True
        
        return False
    
    def create_diagrams_summary(self, has_classes: bool, has_dependencies: bool) -> str:
        """Create a summary of available diagrams"""
        
        summary_lines = [
            "# Диаграммы проекта",
            "",
            "Этот раздел содержит автоматически сгенерированные диаграммы для визуализации архитектуры проекта.",
            ""
        ]
        
        if has_classes:
            summary_lines.extend([
                "## 📊 Диаграмма классов",
                "",
                "Показывает структуру классов, их наследование и основные методы.",
                "",
                "- **Зеленые стрелки**: наследование (extends/implements)",
                "- **Синие блоки**: классы проекта", 
                "- **Методы**: отмечены знаком + (публичные) или - (приватные)",
                ""
            ])
        
        if has_dependencies:
            summary_lines.extend([
                "## 🔗 Граф зависимостей",
                "",
                "Отображает связи между модулями и внешними библиотеками.",
                "",
                "- **Серые блоки**: внешние зависимости",
                "- **Белые блоки**: файлы проекта",
                "- **Стрелки**: направление зависимостей (кто кого импортирует)",
                ""
            ])
        
        if not has_classes and not has_dependencies:
            summary_lines.extend([
                "## ℹ️ Диаграммы недоступны",
                "",
                "В проекте не найдено классов или зависимостей для визуализации.",
                "",
                "Возможные причины:",
                "- Проект состоит из функциональных модулей без классов",
                "- Файлы не содержат импортов",
                "- Поддерживаемые языки программирования не обнаружены",
                ""
            ])
        
        summary_lines.extend([
            "---",
            "",
            "*Диаграммы создаются автоматически при генерации документации*"
        ])
        
        return "\n".join(summary_lines)
