#!/usr/bin/env python3
"""
RepoDoctor - CLI Entry Point

Generates technical documentation for code repositories using LLM analysis.
"""

import argparse
import sys
import os
from pathlib import Path
import logging
from dotenv import load_dotenv

from .generator import DocumentationGenerator

# Load environment variables
load_dotenv()

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Generate technical documentation for code repositories using LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s jsonl2html
  %(prog)s ../my-project --output ./my-project-docs
  %(prog)s /path/to/repo --workers 5 --verbose
        """
    )
    
    parser.add_argument(
        "repo_path",
        nargs='?',
        help="Path to the repository to document"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output directory for documentation (default: repo_path/docs)"
    )
    
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=3,
        help="Number of parallel workers for API calls (default: 3)"
    )
    
    parser.add_argument(
        "--api-key",
        help="OpenRouter API key (can also use OPENROUTER_API_KEY env var)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what files would be documented without generating docs"
    )
    
    parser.add_argument(
        "--docusaurus",
        action="store_true",
        help="Generate Docusaurus site in addition to markdown documentation"
    )
    
    parser.add_argument(
        "--auto-install",
        action="store_true",
        help="Automatically install Docusaurus dependencies (requires --docusaurus)"
    )
    
    parser.add_argument(
        "--auto-start",
        action="store_true",
        help="Automatically start Docusaurus dev server (requires --docusaurus and --auto-install)"
    )
    
    parser.add_argument(
        "--docusaurus-show-hidden",
        action="store_true",
        help="Include hidden files (starting with .) in Docusaurus documentation"
    )
    
    parser.add_argument(
        "--from-docs",
        help="Skip LLM generation and create Docusaurus site from existing docs directory"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Check that either repo_path or --from-docs is provided
    if not args.repo_path and not args.from_docs:
        logger.error("Either repo_path or --from-docs must be provided")
        parser.print_help()
        sys.exit(1)
    
    # Handle --from-docs mode
    if args.from_docs:
        docs_path = Path(args.from_docs)
        if not docs_path.exists():
            logger.error(f"Docs directory does not exist: {docs_path}")
            sys.exit(1)
        
        if not docs_path.is_dir():
            logger.error(f"Docs path is not a directory: {docs_path}")
            sys.exit(1)
        
        # For --from-docs mode, we require --docusaurus
        if not args.docusaurus:
            logger.error("--from-docs requires --docusaurus flag")
            sys.exit(1)
    
    # Validate repository path (only needed if not using --from-docs)
    if not args.from_docs:
        repo_path = Path(args.repo_path)
        if not repo_path.exists():
            logger.error(f"Repository path does not exist: {repo_path}")
            sys.exit(1)
        
        if not repo_path.is_dir():
            logger.error(f"Repository path is not a directory: {repo_path}")
            sys.exit(1)
    
    # Check API key (only needed if not using --from-docs and not dry-run)
    api_key = args.api_key or os.getenv('OPENROUTER_API_KEY')
    if not api_key and not args.dry_run and not args.from_docs:
        logger.error("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    # For dry run or from-docs, we don't need API key - set a dummy one
    if (args.dry_run or args.from_docs) and not api_key:
        api_key = "dummy-key-for-dry-run"
    
    try:
        if args.from_docs:
            # Handle --from-docs mode: create Docusaurus site from existing docs
            from .docusaurus import DocusaurusGenerator
            
            docs_path = Path(args.from_docs)
            
            # Extract project name from docs directory name or use a default
            if docs_path.name.endswith('-docs'):
                project_name = docs_path.name[:-5]  # Remove '-docs' suffix
            elif '-docs-' in docs_path.name:
                # Handle UUID suffixed names like "gonkey-docs-64876fd3"
                project_name = docs_path.name.split('-docs-')[0]
            else:
                project_name = docs_path.name
            
            # Create Docusaurus output path
            if args.output:
                docusaurus_output_path = Path(args.output)
            else:
                # Create output path next to docs directory
                docusaurus_output_path = docs_path.parent / f"{project_name}-docusaurus"
            
            logger.info(f"Creating Docusaurus site from existing docs: {docs_path}")
            logger.info(f"Project name: {project_name}")
            logger.info(f"Output path: {docusaurus_output_path}")
            
            # Create Docusaurus generator
            docusaurus_gen = DocusaurusGenerator(
                docs_path=str(docs_path),
                project_name=project_name,
                output_path=str(docusaurus_output_path),
                show_hidden_files=args.docusaurus_show_hidden
            )
            
            # Generate site
            docusaurus_gen.generate_site(
                auto_install=args.auto_install,
                auto_start=args.auto_start
            )
            docusaurus_gen.create_readme()
            
            logger.info("Docusaurus site created successfully!")
            logger.info(f"Site available at: {docusaurus_output_path}")
            
            if args.auto_install:
                logger.info("Dependencies installed automatically")
            else:
                logger.info("To install dependencies and start:")
                logger.info(f"  cd {docusaurus_output_path}/website")
                logger.info("  npm install")
                logger.info("  npm start")
            
            return
        
        # Normal mode: full documentation generation
        repo_path = Path(args.repo_path)
        
        # Initialize generator
        generator = DocumentationGenerator(
            repo_path=str(repo_path),
            output_path=args.output,
            api_key=api_key
        )
        
        if args.dry_run:
            # Dry run - just show what would be documented
            logger.info("DRY RUN - Scanning for files to document...")
            
            code_files = generator.analyzer.scan_code_files()
            
            if not code_files:
                logger.info("No code files found to document")
                return
            
            logger.info(f"Found {len(code_files)} files that would be documented:")
            for file_path in code_files:
                file_type = generator.analyzer.get_file_type(file_path)
                logger.info(f"  - {file_path} ({file_type})")
            
            # Show dependency analysis
            logger.info("Analyzing dependencies...")
            deps = generator.analyzer.analyze_project_dependencies(code_files)
            
            logger.info("\nDependency summary:")
            for file_path, file_deps in deps.items():
                if file_deps:
                    logger.info(f"  {file_path}: {', '.join(file_deps)}")
                else:
                    logger.info(f"  {file_path}: no dependencies")
            
            logger.info(f"\nDocumentation would be generated in: {generator.output_path}")
            
        else:
            # Generate documentation
            logger.info(f"Starting documentation generation for {repo_path}")
            logger.info(f"Output directory: {generator.output_path}")
            logger.info(f"Max workers: {args.workers}")
            
            generator.generate_documentation(
                max_workers=args.workers,
                enable_docusaurus=args.docusaurus,
                auto_install=args.auto_install,
                auto_start=args.auto_start,
                docusaurus_show_hidden=args.docusaurus_show_hidden
            )
            
            logger.info("Documentation generation completed successfully!")
            logger.info(f"View the documentation at: {generator.output_path / 'README.md'}")
            
            if args.docusaurus:
                docusaurus_path = generator.output_path.parent / f"{generator.project_name}-docusaurus"
                logger.info(f"Docusaurus site available at: {docusaurus_path}")
                logger.info("To start the Docusaurus site:")
                logger.info(f"  cd {docusaurus_path}")
                logger.info("  npm install")
                logger.info("  npm start")
    
    except KeyboardInterrupt:
        logger.info("Documentation generation interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Documentation generation failed: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        sys.exit(1)

if __name__ == "__main__":
    main()
