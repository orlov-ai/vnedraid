import os
import shutil
from pathlib import Path
from typing import Dict, List
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from openrouter_client import OpenRouterClient
from file_analyzer import FileAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentationGenerator:
    """Main class for generating project documentation using LLM"""
    
    def __init__(self, repo_path: str, output_path: str = None, api_key: str = None):
        self.repo_path = Path(repo_path)
        self.output_path = Path(output_path) if output_path else self.repo_path / "docs"
        self.project_name = self.repo_path.name
        
        # Initialize components
        self.client = OpenRouterClient(api_key)
        self.analyzer = FileAnalyzer(repo_path)
        
        # Storage for generated documentation
        self.file_docs = {}
        self.dependency_graph = {}
        
    def generate_documentation(self, max_workers: int = 3) -> None:
        """Generate complete project documentation"""
        logger.info(f"Starting documentation generation for {self.project_name}")
        
        # Step 1: Scan for code files
        logger.info("Scanning for code files...")
        code_files = self.analyzer.scan_code_files()
        
        if not code_files:
            logger.warning("No code files found to document")
            return
        
        # Step 2: Analyze dependencies
        logger.info("Analyzing project dependencies...")
        self.dependency_graph = self.analyzer.analyze_project_dependencies(code_files)
        
        # Step 3: Generate documentation for each file
        logger.info(f"Generating documentation for {len(code_files)} files...")
        self._generate_file_documentations(code_files, max_workers)
        
        # Step 4: Generate project summary
        logger.info("Generating project summary...")
        project_summary = self._generate_project_summary()
        
        # Step 5: Create documentation structure
        logger.info("Creating documentation structure...")
        self._create_documentation_structure(project_summary)
        
        logger.info(f"Documentation generation completed! Output: {self.output_path}")
    
    def _generate_file_documentations(self, files: List[str], max_workers: int) -> None:
        """Generate documentation for all files using parallel processing"""
        
        def generate_single_doc(file_path: str) -> tuple:
            """Generate documentation for a single file"""
            try:
                full_path = self.repo_path / file_path
                
                # Read file content
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Get file type and dependencies
                file_type = self.analyzer.get_file_type(file_path)
                dependencies = self.dependency_graph.get(file_path, [])
                
                # Generate documentation
                doc = self.client.generate_documentation(
                    content=content,
                    file_path=file_path,
                    file_type=file_type,
                    dependencies=dependencies,
                    project_context=f"Проект {self.project_name} - {self._get_project_context()}"
                )
                
                logger.info(f"Generated documentation for {file_path}")
                return file_path, doc
                
            except Exception as e:
                logger.error(f"Failed to generate documentation for {file_path}: {e}")
                return file_path, f"# {file_path}\n\nОшибка генерации документации: {str(e)}"
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(generate_single_doc, file_path): file_path 
                      for file_path in files}
            
            for future in as_completed(futures):
                file_path, doc = future.result()
                self.file_docs[file_path] = doc
                
                # Small delay to avoid rate limiting
                time.sleep(1)
    
    def _generate_project_summary(self) -> str:
        """Generate overall project documentation"""
        try:
            return self.client.generate_project_summary(
                all_docs=self.file_docs,
                dependency_graph=self.dependency_graph,
                project_name=self.project_name
            )
        except Exception as e:
            logger.error(f"Failed to generate project summary: {e}")
            return self._create_fallback_summary()
    
    def _create_documentation_structure(self, project_summary: str) -> None:
        """Create the final documentation directory structure"""
        
        # Create output directory
        if self.output_path.exists():
            shutil.rmtree(self.output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Write main README.md
        readme_content = self._create_main_readme(project_summary)
        (self.output_path / "README.md").write_text(readme_content, encoding='utf-8')
        
        # Create individual file documentation with directory structure
        for file_path, doc_content in self.file_docs.items():
            # Create directory structure that mirrors the original
            doc_file_path = self.output_path / f"{file_path}.md"
            doc_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write documentation file
            doc_file_path.write_text(doc_content, encoding='utf-8')
        
        # Create dependencies graph file
        self._create_dependencies_file()
        
        logger.info(f"Created documentation structure at {self.output_path}")
    
    def _create_main_readme(self, project_summary: str) -> str:
        """Create the main README.md with navigation"""
        
        # Create file tree for navigation
        file_tree = self._create_file_tree()
        
        readme_content = f"""{project_summary}

## Структура документации

Документация организована по структуре исходного проекта. Каждый файл имеет соответствующую документацию:

{file_tree}

## Граф зависимостей

Подробный анализ зависимостей между модулями доступен в файле [dependencies.md](dependencies.md).

## Навигация

- **Основные компоненты**: {self._get_main_components_links()}
- **Конфигурационные файлы**: {self._get_config_files_links()}
- **Тестовые файлы**: {self._get_test_files_links()}

---

*Документация сгенерирована автоматически с помощью LLM анализа кода*
"""
        return readme_content
    
    def _create_file_tree(self) -> str:
        """Create a file tree with links to documentation"""
        lines = []
        
        # Group files by directory
        dir_structure = {}
        for file_path in sorted(self.file_docs.keys()):
            parts = Path(file_path).parts
            current = dir_structure
            
            for part in parts[:-1]:  # directories
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Add file
            current[parts[-1]] = file_path
        
        # Generate tree representation
        def add_tree_level(structure, prefix="", level=0):
            items = sorted(structure.items())
            for i, (name, content) in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                
                if isinstance(content, dict):
                    # Directory
                    lines.append(f"{prefix}{current_prefix}**{name}/**")
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    add_tree_level(content, next_prefix, level + 1)
                else:
                    # File
                    file_link = f"[{name}]({content}.md)"
                    lines.append(f"{prefix}{current_prefix}{file_link}")
        
        add_tree_level(dir_structure)
        return "\n".join(lines)
    
    def _create_dependencies_file(self) -> None:
        """Create dependencies.md file with dependency analysis"""
        
        content = f"""# Граф зависимостей проекта {self.project_name}

## Обзор зависимостей

Данный файл содержит анализ зависимостей между файлами проекта.

## Зависимости по файлам

"""
        
        for file_path, deps in self.dependency_graph.items():
            content += f"### {file_path}\n\n"
            
            if deps:
                content += "**Импортирует:**\n"
                for dep in sorted(deps):
                    content += f"- `{dep}`\n"
            else:
                content += "*Нет внешних зависимостей*\n"
            
            content += "\n"
        
        # Add reverse dependencies (what depends on what)
        reverse_deps = self._calculate_reverse_dependencies()
        if reverse_deps:
            content += "## Обратные зависимости\n\n"
            content += "*Какие файлы используют данный модуль:*\n\n"
            
            for module, dependents in reverse_deps.items():
                if dependents:
                    content += f"### {module}\n\n"
                    content += "**Используется в:**\n"
                    for dependent in sorted(dependents):
                        content += f"- [{dependent}]({dependent}.md)\n"
                    content += "\n"
        
        (self.output_path / "dependencies.md").write_text(content, encoding='utf-8')
    
    def _calculate_reverse_dependencies(self) -> Dict[str, List[str]]:
        """Calculate which files depend on which modules"""
        reverse_deps = {}
        
        for file_path, deps in self.dependency_graph.items():
            for dep in deps:
                if dep not in reverse_deps:
                    reverse_deps[dep] = []
                reverse_deps[dep].append(file_path)
        
        return reverse_deps
    
    def _get_project_context(self) -> str:
        """Get basic project context from common files"""
        context_parts = []
        
        # Check for common project files
        common_files = ['README.md', 'pyproject.toml', 'package.json', 'requirements.txt']
        
        for file_name in common_files:
            file_path = self.repo_path / file_name
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()[:500]  # First 500 chars
                    context_parts.append(f"{file_name}: {content.strip()}")
                except:
                    pass
        
        return " | ".join(context_parts) if context_parts else "Python проект"
    
    def _get_main_components_links(self) -> str:
        """Get links to main component files"""
        main_files = [f for f in self.file_docs.keys() 
                     if any(keyword in f.lower() for keyword in ['main', 'init', 'app', 'core', 'base'])]
        
        if main_files:
            return ", ".join([f"[{Path(f).name}]({f}.md)" for f in main_files[:5]])
        return "Не найдено"
    
    def _get_config_files_links(self) -> str:
        """Get links to configuration files"""
        config_files = [f for f in self.file_docs.keys() 
                       if any(ext in f.lower() for ext in ['.toml', '.json', '.yaml', '.yml', 'config'])]
        
        if config_files:
            return ", ".join([f"[{Path(f).name}]({f}.md)" for f in config_files[:5]])
        return "Не найдено"
    
    def _get_test_files_links(self) -> str:
        """Get links to test files"""
        test_files = [f for f in self.file_docs.keys() if 'test' in f.lower()]
        
        if test_files:
            return ", ".join([f"[{Path(f).name}]({f}.md)" for f in test_files[:5]])
        return "Не найдено"
    
    def _create_fallback_summary(self) -> str:
        """Create a basic summary when LLM generation fails"""
        return f"""# {self.project_name} - Project Documentation

## Обзор проекта

Проект {self.project_name} содержит {len(self.file_docs)} документированных файлов.

## Архитектура

Документация сгенерирована автоматически для следующих компонентов:

{chr(10).join([f"- {file_path}" for file_path in sorted(self.file_docs.keys())])}

## Примечание

Данная документация создана в автоматическом режиме. Подробная документация по каждому файлу доступна в соответствующих разделах.
"""
