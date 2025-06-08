import os
import shutil
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging
import time

logger = logging.getLogger(__name__)

class DocusaurusGenerator:
    """Generate Docusaurus site from markdown documentation"""
    
    def __init__(self, docs_path: str, project_name: str, output_path: str, show_hidden_files: bool = False):
        self.docs_path = Path(docs_path)
        self.project_name = project_name
        self.output_path = Path(output_path)
        self.website_path = self.output_path / "website"
        self.show_hidden_files = show_hidden_files
        
        # Docusaurus configuration
        self.site_config = {
            "title": f"{project_name} Documentation",
            "tagline": f"Автоматически сгенерированная документация для {project_name}",
            "favicon": "img/favicon.ico",
            "url": "https://your-docusaurus-test-site.com",
            "baseUrl": "/",
            "organizationName": "your-org",
            "projectName": project_name,
            "onBrokenLinks": "throw",
            "onBrokenMarkdownLinks": "warn",
            "i18n": {
                "defaultLocale": "ru",
                "locales": ["ru"]
            }
        }
    
    def generate_site(self, auto_install: bool = False, auto_start: bool = False) -> None:
        """Generate complete Docusaurus site"""
        logger.info(f"Generating Docusaurus site at {self.output_path}")
        
        # Step 1: Create Docusaurus project structure
        self._create_docusaurus_structure()
        
        # Step 2: Process and copy markdown files
        self._process_markdown_files()
        
        # Step 3: Generate navigation sidebar
        self._generate_sidebar()
        
        # Step 4: Create configuration files
        self._create_config_files()
        
        # Step 5: Create package.json
        self._create_package_json()
        
        # Step 6: Optional - install dependencies
        if auto_install:
            self._install_dependencies()
            
            # Step 7: Optional - start development server
            if auto_start:
                self._start_dev_server()
        
        logger.info(f"Docusaurus site generated successfully at {self.website_path}")
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if a file should be included in the documentation"""
        # Filter hidden files if the flag is not enabled
        if not self.show_hidden_files and file_path.name.startswith('.'):
            return False
        return True
    
    def _create_docusaurus_structure(self) -> None:
        """Create basic Docusaurus directory structure"""
        
        # Remove existing website directory if it exists, but keep the source docs
        if self.website_path.exists():
            shutil.rmtree(self.website_path)
        
        # Create directory structure
        directories = [
            self.website_path,
            self.website_path / "docs",
            self.website_path / "src" / "components",
            self.website_path / "src" / "pages",
            self.website_path / "static" / "img",
            self.website_path / "blog"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info("Created Docusaurus directory structure")
    
    def _process_markdown_files(self) -> None:
        """Process and copy markdown files to docs directory"""
        
        # Process all markdown files from the docs directory
        for md_file in self.docs_path.rglob("*.md"):
            relative_path = md_file.relative_to(self.docs_path)
            
            # Skip hidden files if the flag is not enabled
            if not self._should_include_file(md_file):
                continue
            
            # Skip README.md as we'll create intro.md
            if relative_path.name == "README.md":
                self._create_intro_from_readme(md_file)
                continue
            
            # Skip files that would create nested docs/ structure
            path_parts = relative_path.parts
            if len(path_parts) > 1 and path_parts[0] == "docs":
                # Skip files that are already in a docs/ subdirectory to prevent nesting
                continue
            
            # Determine target path
            target_path = self.website_path / "docs" / relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Process and copy file
            self._process_single_markdown(md_file, target_path, relative_path)
        
        logger.info("Processed and copied markdown files")
    
    def _create_intro_from_readme(self, readme_path: Path) -> None:
        """Create intro.md from README.md"""
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add Docusaurus frontmatter
        intro_content = f"""---
sidebar_position: 1
slug: /
title: Введение
---

{content}
"""
        
        intro_path = self.website_path / "docs" / "intro.md"
        with open(intro_path, 'w', encoding='utf-8') as f:
            f.write(intro_content)
    
    def _process_single_markdown(self, source_path: Path, target_path: Path, relative_path: Path) -> None:
        """Process a single markdown file and add Docusaurus metadata"""
        
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate title from filename
        title = self._generate_title_from_path(relative_path)
        
        # Generate safe document ID for Docusaurus
        # For files in subdirectories, use just the relative path-based ID without folder prefix
        # Docusaurus will automatically add the folder prefix when creating the composite ID
        doc_id = self._generate_safe_doc_id(relative_path)
        
        # Create frontmatter
        frontmatter = f"""---
id: {doc_id}
title: {title}
---

"""
        
        # Combine and write
        final_content = frontmatter + content
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
    
    def _generate_title_from_path(self, path: Path) -> str:
        """Generate a readable title from file path"""
        
        # Remove .md extension
        name = path.stem
        
        # Handle special cases
        if name == "dependencies":
            return "Граф зависимостей"
        
        # For files like "file.py.md", use "file.py"
        if name.endswith('.py'):
            return name
        if name.endswith('.js'):
            return name
        if name.endswith('.ts'):
            return name
        
        # Default: use filename as-is
        return name
    
    def _generate_safe_doc_id(self, path: Path) -> str:
        """Generate a safe document ID for Docusaurus"""
        
        # Convert path to string and remove .md extension
        path_str = str(path.with_suffix(''))
        
        # Replace all problematic characters including slashes with dashes
        safe_id = path_str.replace('/', '-').replace('\\', '-').replace('.', '-')
        
        # Remove multiple consecutive dashes
        while '--' in safe_id:
            safe_id = safe_id.replace('--', '-')
        
        # Remove leading/trailing dashes
        safe_id = safe_id.strip('-')
        
        return safe_id
    
    def _generate_sidebar(self) -> None:
        """Generate sidebar configuration"""
        
        # Scan docs directory to build sidebar structure
        sidebar_items = []
        
        # Add intro first
        sidebar_items.append({
            "type": "doc",
            "id": "intro",
            "label": "Введение"
        })
        
        # Add dependencies
        deps_path = self.website_path / "docs" / "dependencies.md"
        if deps_path.exists():
            sidebar_items.append({
                "type": "doc", 
                "id": "dependencies",
                "label": "Граф зависимостей"
            })
        
        # Group other files by directory
        docs_dir = self.website_path / "docs"
        categories = self._build_sidebar_categories(docs_dir)
        sidebar_items.extend(categories)
        
        # Create sidebar.ts
        sidebar_content = f"""import type {{SidebarsConfig}} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {{
  tutorialSidebar: {json.dumps(sidebar_items, indent=4, ensure_ascii=False)},
}};

export default sidebars;
"""
        
        sidebar_path = self.website_path / "sidebars.ts"
        with open(sidebar_path, 'w', encoding='utf-8') as f:
            f.write(sidebar_content)
    
    def _build_sidebar_categories(self, docs_dir: Path) -> List[Dict]:
        """Build sidebar categories from directory structure"""
        categories = []
        
        # Scan for subdirectories
        for item in docs_dir.iterdir():
            if item.is_dir():
                category = self._build_category(item, docs_dir)
                if category:
                    categories.append(category)
        
        # Add individual files that aren't in subdirectories
        individual_files = []
        for md_file in docs_dir.glob("*.md"):
            if md_file.name not in ["intro.md", "dependencies.md"]:
                # Skip hidden files if the flag is not enabled
                if not self._should_include_file(md_file):
                    continue
                
                # Use the same ID generation logic as in _process_single_markdown
                relative_path = md_file.relative_to(docs_dir)
                doc_id = self._generate_safe_doc_id(relative_path)
                title = self._generate_title_from_path(relative_path)
                individual_files.append({
                    "type": "doc",
                    "id": doc_id,
                    "label": title
                })
        
        if individual_files:
            categories.extend(individual_files)
        
        return categories
    
    def _build_category(self, category_dir: Path, docs_dir: Path) -> Optional[Dict]:
        """Build a category from a directory"""
        
        items = []
        
        # Add files in this directory
        for md_file in category_dir.glob("*.md"):
            relative_path = md_file.relative_to(docs_dir)
            
            # Skip hidden files if the flag is not enabled
            if not self._should_include_file(md_file):
                continue
            
            # Skip __init__.py files as Docusaurus often ignores them
            if '__init__.py' in str(relative_path):
                continue
            
            # Read the actual ID from the file's frontmatter
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract ID from frontmatter
                    if content.startswith('---'):
                        frontmatter_end = content.find('---', 3)
                        if frontmatter_end != -1:
                            frontmatter = content[3:frontmatter_end]
                            for line in frontmatter.split('\n'):
                                if line.strip().startswith('id:'):
                                    file_id = line.split(':', 1)[1].strip()
                                    break
                            else:
                                file_id = self._generate_safe_doc_id(relative_path)
                        else:
                            file_id = self._generate_safe_doc_id(relative_path)
                    else:
                        file_id = self._generate_safe_doc_id(relative_path)
            except:
                file_id = self._generate_safe_doc_id(relative_path)
            
            # For files in subdirectories, Docusaurus creates composite IDs like "category/file-id"
            category_name = category_dir.name
            doc_id = f"{category_name}/{file_id}"
            
            title = self._generate_title_from_path(relative_path)
            
            items.append({
                "type": "doc",
                "id": doc_id,
                "label": title
            })
        
        # Add subdirectories recursively
        for subdir in category_dir.iterdir():
            if subdir.is_dir():
                subcategory = self._build_category(subdir, docs_dir)
                if subcategory:
                    items.append(subcategory)
        
        if not items:
            return None
        
        return {
            "type": "category",
            "label": category_dir.name,
            "items": items
        }
    
    def _create_config_files(self) -> None:
        """Create Docusaurus configuration files"""
        
        # Create docusaurus.config.ts
        config_content = f"""import {{themes as prismThemes}} from 'prism-react-renderer';
import type {{Config}} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {{
  title: '{self.site_config["title"]}',
  tagline: '{self.site_config["tagline"]}',
  favicon: '{self.site_config["favicon"]}',

  url: '{self.site_config["url"]}',
  baseUrl: '{self.site_config["baseUrl"]}',

  organizationName: '{self.site_config["organizationName"]}',
  projectName: '{self.site_config["projectName"]}',

  onBrokenLinks: '{self.site_config["onBrokenLinks"]}',
  onBrokenMarkdownLinks: '{self.site_config["onBrokenMarkdownLinks"]}',

  i18n: {{
    defaultLocale: '{self.site_config["i18n"]["defaultLocale"]}',
    locales: {json.dumps(self.site_config["i18n"]["locales"])},
  }},

  presets: [
    [
      'classic',
      {{
        docs: {{
          sidebarPath: './sidebars.ts',
          routeBasePath: '/',
        }},
        blog: false,
        theme: {{
          customCss: './src/css/custom.css',
        }},
      }} satisfies Preset.Options,
    ],
  ],

  themeConfig: {{
    navbar: {{
      title: '{self.project_name}',
      items: [
        {{
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Документация',
        }},
      ],
    }},
    footer: {{
      style: 'dark',
      copyright: `Документация сгенерирована автоматически`,
    }},
    prism: {{
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'javascript', 'typescript', 'java', 'rust', 'go'],
    }},
  }} satisfies Preset.ThemeConfig,
}};

export default config;
"""
        
        config_path = self.website_path / "docusaurus.config.ts"
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        # Create TypeScript config
        tsconfig_content = """{
  "extends": "@docusaurus/tsconfig",
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@site/*": ["./src/*"],
      "@generated/*": ["./.docusaurus/*"]
    }
  },
  "include": [
    "src/",
    "docs/",
    "docusaurus.config.ts"
  ]
}
"""
        
        tsconfig_path = self.website_path / "tsconfig.json"
        with open(tsconfig_path, 'w', encoding='utf-8') as f:
            f.write(tsconfig_content)
        
        # Create custom CSS
        css_content = """/**
 * Any CSS included here will be global. The classic template
 * bundles Infima by default. Infima is a CSS framework designed to
 * work well for content-centric websites.
 */

/* You can override the default Infima variables here. */
:root {
  --ifm-color-primary: #2e8555;
  --ifm-color-primary-dark: #29784c;
  --ifm-color-primary-darker: #277148;
  --ifm-color-primary-darkest: #205d3b;
  --ifm-color-primary-light: #33925d;
  --ifm-color-primary-lighter: #359962;
  --ifm-color-primary-lightest: #3cad6e;
  --ifm-code-font-size: 95%;
  --docusaurus-highlighted-code-line-bg: rgba(0, 0, 0, 0.1);
}

/* For readability improvements */
[data-theme='dark'] {
  --docusaurus-highlighted-code-line-bg: rgba(0, 0, 0, 0.3);
}
"""
        
        css_dir = self.website_path / "src" / "css"
        css_dir.mkdir(parents=True, exist_ok=True)
        css_path = css_dir / "custom.css"
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
    
    def _create_package_json(self) -> None:
        """Create package.json for Docusaurus site"""
        
        package_json = {
            "name": f"{self.project_name}-docs",
            "version": "0.0.0",
            "private": True,
            "scripts": {
                "docusaurus": "docusaurus",
                "start": "docusaurus start",
                "build": "docusaurus build",
                "swizzle": "docusaurus swizzle",
                "deploy": "docusaurus deploy",
                "clear": "docusaurus clear",
                "serve": "docusaurus serve",
                "write-translations": "docusaurus write-translations",
                "write-heading-ids": "docusaurus write-heading-ids"
            },
            "dependencies": {
                "@docusaurus/core": "3.0.1",
                "@docusaurus/preset-classic": "3.0.1",
                "@docusaurus/tsconfig": "3.0.1",
                "@mdx-js/react": "^3.0.0",
                "clsx": "^2.0.0",
                "prism-react-renderer": "^2.3.0",
                "react": "^18.0.0",
                "react-dom": "^18.0.0"
            },
            "devDependencies": {
                "@docusaurus/module-type-aliases": "3.0.1",
                "@docusaurus/types": "3.0.1",
                "typescript": "~5.2.2"
            },
            "browserslist": {
                "production": [
                    ">0.5%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            },
            "engines": {
                "node": ">=18.0"
            }
        }
        
        package_path = self.website_path / "package.json"
        with open(package_path, 'w', encoding='utf-8') as f:
            json.dump(package_json, f, indent=2, ensure_ascii=False)
    
    def _install_dependencies(self) -> None:
        """Install npm dependencies"""
        logger.info("Installing npm dependencies...")
        
        try:
            result = subprocess.run(
                ["npm", "install"],
                cwd=self.website_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                logger.info("Dependencies installed successfully")
            else:
                logger.error(f"Failed to install dependencies: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("npm install timed out after 5 minutes")
        except FileNotFoundError:
            logger.error("npm not found. Please install Node.js and npm")
        except Exception as e:
            logger.error(f"Error installing dependencies: {e}")
    
    def _start_dev_server(self) -> None:
        """Start Docusaurus development server"""
        logger.info("Starting Docusaurus development server...")
        
        try:
            # Start in background
            process = subprocess.Popen(
                ["npm", "start"],
                cwd=self.website_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info(f"Development server started with PID {process.pid}")
            logger.info("Server should be available at http://localhost:3000")
            logger.info("Press Ctrl+C to stop the server")
            
            # Wait a bit to see if it starts successfully
            time.sleep(3)
            if process.poll() is None:
                logger.info("Server appears to be running successfully")
            else:
                stdout, stderr = process.communicate()
                logger.error(f"Server failed to start: {stderr}")
                
        except FileNotFoundError:
            logger.error("npm not found. Please install Node.js and npm")
        except Exception as e:
            logger.error(f"Error starting development server: {e}")
    
    def create_readme(self) -> None:
        """Create README.md for the Docusaurus project"""
        
        readme_content = f"""# {self.project_name} - Docusaurus Documentation

Этот проект содержит автоматически сгенерированную документацию в формате Docusaurus.

## Быстрый старт

### Установка зависимостей

```bash
cd website
npm install
```

### Запуск сервера разработки

```bash
npm start
```

Сайт будет доступен по адресу http://localhost:3000

### Сборка для продакшена

```bash
npm run build
```

Результат сборки будет в папке `website/build/`.

## Структура проекта

```
{self.project_name}-docusaurus/
├── website/
│   ├── docs/           # Документация в markdown
│   ├── src/            # Исходники React компонентов
│   ├── static/         # Статические файлы
│   ├── docusaurus.config.ts  # Конфигурация
│   ├── sidebars.ts     # Структура сайдбара
│   └── package.json    # Зависимости
└── README.md          # Этот файл
```

## Редактирование документации

1. Измените markdown файлы в папке `website/docs/`
2. Обновите `sidebars.ts` если добавили новые файлы
3. Перезапустите сервер разработки

## Деплой

Для деплоя на GitHub Pages или другой статический хостинг:

```bash
npm run build
# Загрузите содержимое website/build/ на хостинг
```

## Автогенерация

Эта документация была автоматически сгенерирована из исходного кода проекта {self.project_name}.

Для обновления документации запустите генератор документации заново:

```bash
python main.py /path/to/{self.project_name} --docusaurus --auto-install
```
"""
        
        readme_path = self.output_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
