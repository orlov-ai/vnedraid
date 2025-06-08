#!/usr/bin/env node

/**
 * RepoDoctor MCP Server
 * 
 * An MCP server that provides access to generated documentation from RepoDoctor.
 * Allows querying documentation files, project summaries, and dependency graphs.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
  ListPromptsRequestSchema,
  GetPromptRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { spawn } from "child_process";
import * as fs from "fs";
import * as path from "path";

/**
 * Type definitions
 */
interface DocumentationProject {
  name: string;
  path: string;
  files: string[];
  hasReadme: boolean;
  hasDependencies: boolean;
  hasDiagrams: boolean;
}

interface QueryResult {
  query: string;
  results: Array<{
    file: string;
    content: string;
    relevance: number;
  }>;
}

/**
 * In-memory storage for discovered documentation projects
 */
let documentationProjects: { [projectName: string]: DocumentationProject } = {};

/**
 * Helper function to scan for documentation directories
 */
function scanForDocumentationProjects(basePath: string): void {
  documentationProjects = {};
  
  try {
    const entries = fs.readdirSync(basePath, { withFileTypes: true });
    
    for (const entry of entries) {
      if (entry.isDirectory() && entry.name.includes('-docs-')) {
        const projectPath = path.join(basePath, entry.name);
        const projectName = entry.name.split('-docs-')[0];
        
        try {
          const files = getAllMarkdownFiles(projectPath);
          const hasReadme = files.some(f => f.includes('README.md'));
          const hasDependencies = files.some(f => f.includes('dependencies.md'));
          const hasDiagrams = files.some(f => f.includes('diagrams.md'));
          
          documentationProjects[projectName] = {
            name: projectName,
            path: projectPath,
            files,
            hasReadme,
            hasDependencies,
            hasDiagrams
          };
        } catch (error) {
          console.error(`Error scanning project ${entry.name}:`, error);
        }
      }
    }
  } catch (error) {
    console.error('Error scanning for documentation projects:', error);
  }
}

/**
 * Recursively get all markdown files in a directory
 */
function getAllMarkdownFiles(dirPath: string): string[] {
  const files: string[] = [];
  
  try {
    const entries = fs.readdirSync(dirPath, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(dirPath, entry.name);
      
      if (entry.isDirectory()) {
        files.push(...getAllMarkdownFiles(fullPath));
      } else if (entry.name.endsWith('.md')) {
        files.push(fullPath);
      }
    }
  } catch (error) {
    console.error(`Error reading directory ${dirPath}:`, error);
  }
  
  return files;
}

/**
 * Search documentation content for a query
 */
function searchDocumentation(projectName: string, query: string): QueryResult {
  const project = documentationProjects[projectName];
  if (!project) {
    throw new Error(`Project ${projectName} not found`);
  }
  
  const results = [];
  const queryLower = query.toLowerCase();
  
  for (const filePath of project.files) {
    try {
      const content = fs.readFileSync(filePath, 'utf-8');
      const contentLower = content.toLowerCase();
      
      // Simple relevance scoring based on query matches
      const matches = (contentLower.match(new RegExp(queryLower, 'g')) || []).length;
      
      if (matches > 0) {
        // Get context around matches
        const lines = content.split('\n');
        const relevantLines = [];
        
        for (let i = 0; i < lines.length; i++) {
          if (lines[i].toLowerCase().includes(queryLower)) {
            // Include context: 2 lines before and after
            const start = Math.max(0, i - 2);
            const end = Math.min(lines.length, i + 3);
            relevantLines.push(...lines.slice(start, end));
          }
        }
        
        results.push({
          file: path.relative(project.path, filePath),
          content: relevantLines.join('\n'),
          relevance: matches
        });
      }
    } catch (error) {
      console.error(`Error reading file ${filePath}:`, error);
    }
  }
  
  // Sort by relevance (descending)
  results.sort((a, b) => b.relevance - a.relevance);
  
  return {
    query,
    results: results.slice(0, 10) // Limit to top 10 results
  };
}

/**
 * Initialize the server by scanning for documentation projects
 */
function initializeServer() {
  // Scan current working directory and common locations
  const scanPaths = [
    process.cwd(),
    path.join(process.cwd(), 'data'),
    path.join(process.cwd(), 'vnedraid'),
    '/Users/alex/Projects/Внедрейд-2025/data'
  ];
  
  for (const scanPath of scanPaths) {
    if (fs.existsSync(scanPath)) {
      scanForDocumentationProjects(scanPath);
    }
  }
  
  console.error(`Discovered ${Object.keys(documentationProjects).length} documentation projects`);
}

/**
 * Create an MCP server with capabilities for resources, tools, and prompts
 */
const server = new Server(
  {
    name: "repodoctor-server",
    version: "0.1.0",
  },
  {
    capabilities: {
      resources: {},
      tools: {},
      prompts: {},
    },
  }
);

/**
 * Handler for listing available documentation projects as resources
 */
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  const resources = [];
  
  for (const [projectName, project] of Object.entries(documentationProjects)) {
    // Add main project resource
    resources.push({
      uri: `repodoctor://project/${projectName}`,
      mimeType: "text/markdown",
      name: `${projectName} - Project Overview`,
      description: `Complete documentation for ${projectName} project`
    });
    
    // Add README if available
    if (project.hasReadme) {
      resources.push({
        uri: `repodoctor://project/${projectName}/readme`,
        mimeType: "text/markdown",
        name: `${projectName} - README`,
        description: `Main README for ${projectName}`
      });
    }
    
    // Add dependencies if available
    if (project.hasDependencies) {
      resources.push({
        uri: `repodoctor://project/${projectName}/dependencies`,
        mimeType: "text/markdown",
        name: `${projectName} - Dependencies`,
        description: `Dependency graph for ${projectName}`
      });
    }
    
    // Add diagrams if available
    if (project.hasDiagrams) {
      resources.push({
        uri: `repodoctor://project/${projectName}/diagrams`,
        mimeType: "text/markdown",
        name: `${projectName} - Diagrams`,
        description: `Architecture diagrams for ${projectName}`
      });
    }
  }
  
  return { resources };
});

/**
 * Handler for reading specific documentation resources
 */
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const url = new URL(request.params.uri);
  const pathParts = url.pathname.split('/').filter(p => p);
  
  if (pathParts.length < 2 || pathParts[0] !== 'project') {
    throw new Error('Invalid resource URI');
  }
  
  const projectName = pathParts[1];
  const resourceType = pathParts[2] || 'overview';
  
  const project = documentationProjects[projectName];
  if (!project) {
    throw new Error(`Project ${projectName} not found`);
  }
  
  let content = '';
  
  try {
    switch (resourceType) {
      case 'overview':
        // Return a summary of all available documentation
        content = `# ${projectName} - Documentation Overview\n\n`;
        content += `Available documentation files:\n\n`;
        for (const filePath of project.files) {
          const relativePath = path.relative(project.path, filePath);
          content += `- ${relativePath}\n`;
        }
        break;
        
      case 'readme':
        const readmePath = project.files.find(f => f.includes('README.md'));
        if (readmePath) {
          content = fs.readFileSync(readmePath, 'utf-8');
        } else {
          throw new Error('README not found');
        }
        break;
        
      case 'dependencies':
        const depsPath = project.files.find(f => f.includes('dependencies.md'));
        if (depsPath) {
          content = fs.readFileSync(depsPath, 'utf-8');
        } else {
          throw new Error('Dependencies file not found');
        }
        break;
        
      case 'diagrams':
        const diagramsPath = project.files.find(f => f.includes('diagrams.md'));
        if (diagramsPath) {
          content = fs.readFileSync(diagramsPath, 'utf-8');
        } else {
          throw new Error('Diagrams file not found');
        }
        break;
        
      default:
        throw new Error(`Unknown resource type: ${resourceType}`);
    }
  } catch (error) {
    throw new Error(`Error reading resource: ${error instanceof Error ? error.message : String(error)}`);
  }
  
  return {
    contents: [{
      uri: request.params.uri,
      mimeType: "text/markdown",
      text: content
    }]
  };
});

/**
 * Handler for listing available tools
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "search_documentation",
        description: "Search through documentation content for specific information",
        inputSchema: {
          type: "object",
          properties: {
            project: {
              type: "string",
              description: "Name of the project to search in",
              enum: Object.keys(documentationProjects)
            },
            query: {
              type: "string",
              description: "Search query (keywords, function names, concepts, etc.)"
            }
          },
          required: ["project", "query"]
        }
      },
      {
        name: "generate_documentation",
        description: "Generate new documentation for a project using RepoDoctor",
        inputSchema: {
          type: "object",
          properties: {
            project_path: {
              type: "string",
              description: "Path to the project to document"
            },
            output_path: {
              type: "string",
              description: "Optional output path (defaults to project_path/docs)"
            },
            include_docusaurus: {
              type: "boolean",
              description: "Whether to generate Docusaurus site",
              default: false
            }
          },
          required: ["project_path"]
        }
      },
      {
        name: "refresh_projects",
        description: "Refresh the list of available documentation projects",
        inputSchema: {
          type: "object",
          properties: {},
          additionalProperties: false
        }
      }
    ]
  };
});

/**
 * Handler for tool calls
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  switch (request.params.name) {
    case "search_documentation": {
      const project = String(request.params.arguments?.project);
      const query = String(request.params.arguments?.query);
      
      if (!project || !query) {
        throw new Error("Project and query are required");
      }
      
      try {
        const result = searchDocumentation(project, query);
        
        let response = `# Search Results for "${query}" in ${project}\n\n`;
        response += `Found ${result.results.length} relevant sections:\n\n`;
        
        for (const [index, item] of result.results.entries()) {
          response += `## Result ${index + 1}: ${item.file}\n`;
          response += `**Relevance Score:** ${item.relevance}\n\n`;
          response += '```markdown\n';
          response += item.content;
          response += '\n```\n\n';
        }
        
        return {
          content: [{
            type: "text",
            text: response
          }]
        };
      } catch (error) {
        throw new Error(`Search failed: ${error instanceof Error ? error.message : String(error)}`);
      }
    }
    
    case "generate_documentation": {
      const projectPath = String(request.params.arguments?.project_path);
      const outputPath = request.params.arguments?.output_path ? String(request.params.arguments.output_path) : undefined;
      const includeDocusaurus = Boolean(request.params.arguments?.include_docusaurus);
      
      if (!projectPath) {
        throw new Error("Project path is required");
      }
      
      return new Promise((resolve, reject) => {
        // Build command
        const args = ['-m', 'vnedraid.repodoctor.cli', projectPath];
        if (outputPath) {
          args.push('--output', outputPath);
        }
        if (includeDocusaurus) {
          args.push('--docusaurus');
        }
        
        const process = spawn('python3', args, {
          cwd: '/Users/alex/Projects/Внедрейд-2025',
          stdio: ['pipe', 'pipe', 'pipe']
        });
        
        let stdout = '';
        let stderr = '';
        
        process.stdout.on('data', (data) => {
          stdout += data.toString();
        });
        
        process.stderr.on('data', (data) => {
          stderr += data.toString();
        });
        
        process.on('close', (code) => {
          if (code === 0) {
            // Refresh projects after successful generation
            initializeServer();
            
            resolve({
              content: [{
                type: "text",
                text: `Documentation generated successfully!\n\nOutput:\n${stdout}\n\nErrors (if any):\n${stderr}`
              }]
            });
          } else {
            reject(new Error(`Documentation generation failed with code ${code}:\n${stderr}`));
          }
        });
      });
    }
    
    case "refresh_projects": {
      initializeServer();
      
      const projectList = Object.keys(documentationProjects).join(', ');
      
      return {
        content: [{
          type: "text",
          text: `Refreshed documentation projects. Found: ${projectList || 'None'}`
        }]
      };
    }
    
    default:
      throw new Error("Unknown tool");
  }
});

/**
 * Handler for listing available prompts
 */
server.setRequestHandler(ListPromptsRequestSchema, async () => {
  return {
    prompts: [
      {
        name: "analyze_project_architecture",
        description: "Analyze project architecture based on documentation",
        arguments: [
          {
            name: "project",
            description: "Project name to analyze",
            required: true
          }
        ]
      },
      {
        name: "explain_dependencies",
        description: "Explain project dependencies and their relationships",
        arguments: [
          {
            name: "project",
            description: "Project name to explain dependencies for",
            required: true
          }
        ]
      }
    ]
  };
});

/**
 * Handler for prompts
 */
server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  const projectName = request.params.arguments?.project as string;
  
  if (!projectName || !documentationProjects[projectName]) {
    throw new Error(`Project ${projectName} not found`);
  }
  
  const project = documentationProjects[projectName];
  
  switch (request.params.name) {
    case "analyze_project_architecture":
      const resources = [];
      
      // Include README
      if (project.hasReadme) {
        const readmePath = project.files.find(f => f.includes('README.md'));
        if (readmePath) {
          const content = fs.readFileSync(readmePath, 'utf-8');
          resources.push({
            type: "resource" as const,
            resource: {
              uri: `repodoctor://project/${projectName}/readme`,
              mimeType: "text/markdown",
              text: content
            }
          });
        }
      }
      
      // Include diagrams
      if (project.hasDiagrams) {
        const diagramsPath = project.files.find(f => f.includes('diagrams.md'));
        if (diagramsPath) {
          const content = fs.readFileSync(diagramsPath, 'utf-8');
          resources.push({
            type: "resource" as const,
            resource: {
              uri: `repodoctor://project/${projectName}/diagrams`,
              mimeType: "text/markdown",
              text: content
            }
          });
        }
      }
      
      return {
        messages: [
          {
            role: "user",
            content: {
              type: "text",
              text: `Please analyze the architecture of the ${projectName} project based on the following documentation:`
            }
          },
          ...resources.map(resource => ({
            role: "user" as const,
            content: resource
          })),
          {
            role: "user",
            content: {
              type: "text",
              text: "Provide a comprehensive analysis of:\n1. Overall architecture and design patterns\n2. Key components and their responsibilities\n3. Data flow and dependencies\n4. Strengths and potential areas for improvement"
            }
          }
        ]
      };
      
    case "explain_dependencies":
      if (!project.hasDependencies) {
        throw new Error(`No dependency information available for ${projectName}`);
      }
      
      const depsPath = project.files.find(f => f.includes('dependencies.md'));
      if (!depsPath) {
        throw new Error(`Dependencies file not found for ${projectName}`);
      }
      
      const depsContent = fs.readFileSync(depsPath, 'utf-8');
      
      return {
        messages: [
          {
            role: "user",
            content: {
              type: "text",
              text: `Please explain the dependencies and their relationships for the ${projectName} project:`
            }
          },
          {
            role: "user",
            content: {
              type: "resource",
              resource: {
                uri: `repodoctor://project/${projectName}/dependencies`,
                mimeType: "text/markdown",
                text: depsContent
              }
            }
          },
          {
            role: "user",
            content: {
              type: "text",
              text: "Explain:\n1. Key external dependencies and their purposes\n2. Internal module relationships\n3. Potential dependency risks or improvements\n4. Architecture insights from the dependency graph"
            }
          }
        ]
      };
      
    default:
      throw new Error("Unknown prompt");
  }
});

/**
 * Start the server
 */
async function main() {
  // Initialize by scanning for documentation projects
  initializeServer();
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
