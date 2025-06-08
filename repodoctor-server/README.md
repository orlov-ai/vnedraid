# RepoDoctor MCP Server

An MCP (Model Context Protocol) server that provides access to generated documentation from RepoDoctor. This server allows AI assistants to query documentation, search through project files, and generate new documentation for code repositories.

## Features

- **Documentation Access**: Browse and read generated documentation from RepoDoctor
- **Smart Search**: Search through documentation content with relevance scoring
- **Dynamic Generation**: Generate new documentation for projects on-demand
- **Multi-project Support**: Manage documentation for multiple projects simultaneously
- **Structured Resources**: Access project overviews, dependencies, and architecture diagrams

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
npm install
```

3. Build the TypeScript code:

```bash
npm run build
```

## Usage

### As a Standalone MCP Server

To run the server in standalone mode:

```bash
npm start
```

### Integration with Cline

To use this server with Cline, add it to your MCP server configuration:

1. Open Cline settings
2. Go to MCP Servers
3. Add a new server with the following configuration:

```json
{
  "command": "node",
  "args": ["/path/to/repodoctor-server/build/index.js"],
  "cwd": "/path/to/repodoctor-server"
}
```

## Available Tools

### `search_documentation`
Search through documentation content for specific information.

**Parameters:**
- `project` (string): Name of the project to search in
- `query` (string): Search query (keywords, function names, concepts, etc.)

**Example:**
```json
{
  "project": "my-project",
  "query": "authentication"
}
```

### `generate_documentation`
Generate new documentation for a project using RepoDoctor.

**Parameters:**
- `project_path` (string): Path to the project to document
- `output_path` (string, optional): Output path (defaults to project_path/docs)
- `include_docusaurus` (boolean, optional): Whether to generate Docusaurus site

**Example:**
```json
{
  "project_path": "/path/to/my-project",
  "include_docusaurus": true
}
```

### `refresh_projects`
Refresh the list of available documentation projects.

**Parameters:** None

## Available Resources

### Project Overview
- URI: `repodoctor://project/{project_name}`
- Description: Complete documentation overview for a project

### Project README
- URI: `repodoctor://project/{project_name}/readme`
- Description: Main README documentation

### Dependencies
- URI: `repodoctor://project/{project_name}/dependencies`
- Description: Project dependency graph and analysis

### Diagrams
- URI: `repodoctor://project/{project_name}/diagrams`
- Description: Architecture and class diagrams

## Available Prompts

### `analyze_project_architecture`
Analyze project architecture based on documentation.

**Arguments:**
- `project` (required): Project name to analyze

### `explain_dependencies`
Explain project dependencies and their relationships.

**Arguments:**
- `project` (required): Project name to explain dependencies for

## Configuration

The server automatically scans for documentation projects in:
- Current working directory
- `./data` subdirectory
- `./vnedraid` subdirectory
- `/Users/alex/Projects/Внедрейд-2025/data` (configurable)

Documentation projects are identified by directory names containing `-docs-` pattern.

## Development

### Build
```bash
npm run build
```

### Watch Mode
```bash
npm run dev
```

### Clean Build
```bash
npm run clean && npm run build
```

## Project Structure

```
repodoctor-server/
├── src/
│   └── index.ts          # Main server implementation
├── build/                # Compiled JavaScript (generated)
├── package.json          # Node.js dependencies and scripts
├── tsconfig.json         # TypeScript configuration
└── README.md            # This file
```

## Requirements

- Node.js 18.0.0 or higher
- RepoDoctor installed and accessible via Python
- Generated documentation projects (created by RepoDoctor)

## Example Usage with Cline

Once configured, you can ask Cline questions like:

- "Search for authentication code in my-project"
- "Show me the dependencies for the poseidon project"
- "Generate documentation for /path/to/new-project"
- "Analyze the architecture of the php-metrics project"

The server will automatically discover available documentation projects and provide intelligent responses based on the generated documentation.

## Troubleshooting

### No Projects Found
If no documentation projects are discovered:
1. Ensure RepoDoctor has been run on your projects
2. Check that documentation directories follow the `-docs-` naming pattern
3. Verify the scan paths in the server configuration

### Search Not Working
If search returns no results:
1. Verify the project name matches exactly
2. Check that the documentation files contain the search terms
3. Try broader search terms

### Generation Fails
If documentation generation fails:
1. Ensure Python and RepoDoctor are properly installed
2. Check that the project path exists and is accessible
3. Verify API keys are configured for RepoDoctor

## License

MIT License - see LICENSE file for details.
