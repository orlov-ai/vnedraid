import os
import requests
import json
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenRouterClient:
    """Client for OpenRouter API to generate documentation using Gemini 2.5 Pro"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.base_url = os.getenv('OPENAI_BASE_URL', 'https://openrouter.ai/api/v1')
        self.model = "google/gemini-2.5-flash-preview-05-20"
        
        if not self.api_key:
            raise ValueError("OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable.")
    
    def generate_documentation(self, content: str, file_path: str, file_type: str, 
                             dependencies: list = None, project_context: str = "") -> str:
        """Generate technical documentation for a code file using Gemini"""
        
        prompt = self._create_file_documentation_prompt(
            content, file_path, file_type, dependencies or [], project_context
        )
        
        return self._call_api(prompt)
    
    def generate_project_summary(self, all_docs: dict, dependency_graph: dict, 
                               project_name: str) -> str:
        """Generate overall project documentation"""
        
        prompt = self._create_project_summary_prompt(all_docs, dependency_graph, project_name)
        return self._call_api(prompt)
    
    def _create_file_documentation_prompt(self, content: str, file_path: str, 
                                        file_type: str, dependencies: list, 
                                        project_context: str) -> str:
        """Create prompt for individual file documentation"""
        
        deps_text = "\n".join(f"- {dep}" for dep in dependencies) if dependencies else "Нет внешних зависимостей"
        
        return f"""Проанализируй код файла {file_path} и создай техническую документацию в markdown формате.

ОБЯЗАТЕЛЬНО включи:
1. # {file_path} - заголовок с именем файла
2. ## Назначение - краткое описание назначения файла
3. ## Основные компоненты - классы, функции, константы с описанием
4. ## Зависимости - импорты и их назначение
5. ## Архитектурные решения - паттерны, подходы
6. ## API/Интерфейсы - публичные методы и их сигнатуры
7. ## Примеры использования - если применимо

Тип файла: {file_type}
Контекст проекта: {project_context}

Зависимости файла:
{deps_text}

Код файла:
```{file_type}
{content}
```

Отвечай ТОЛЬКО markdown документацией, без дополнительных комментариев."""

    def _create_project_summary_prompt(self, all_docs: dict, dependency_graph: dict, 
                                     project_name: str) -> str:
        """Create prompt for project summary documentation"""
        
        files_summary = "\n\n".join([f"## {path}\n{doc[:500]}..." for path, doc in all_docs.items()])
        
        deps_text = "\n".join([
            f"**{file}**: {', '.join(deps) if deps else 'Нет зависимостей'}" 
            for file, deps in dependency_graph.items()
        ])
        
        return f"""На основе документации всех файлов проекта {project_name} создай общее техническое описание в markdown формате.

ОБЯЗАТЕЛЬНО включи:
1. # {project_name} - Project Documentation
2. ## Обзор проекта - общее назначение и функциональность
3. ## Архитектура - структура проекта и основные компоненты
4. ## Основные модули - описание ключевых частей
5. ## Граф зависимостей - как модули связаны друг с другом
6. ## Точки входа - entry points и основные API
7. ## Структура файлов - навигация по документации

Документация отдельных файлов:
{files_summary}

Граф зависимостей:
{deps_text}

Отвечай ТОЛЬКО markdown документацией, без дополнительных комментариев."""

    def _call_api(self, prompt: str) -> str:
        """Make API call to OpenRouter"""
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        data = {
            'model': self.model,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.3,
            'max_tokens': 4000
        }
        
        try:
            logger.info(f"Calling OpenRouter API with model {self.model}")
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
        except KeyError as e:
            logger.error(f"Unexpected API response format: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
