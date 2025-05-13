import os
import sys
import click
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 기본 설정값
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 3000
DEFAULT_MONGODB_URL = "mongodb://localhost:27017/admin"

# CLI 그룹 정의
@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--transport', type=click.Choice(['http', 'sse']), default='http',
              help='Transport type for MCP server (http or sse)')
@click.option('--host', default=DEFAULT_HOST,
              help=f'Host to bind the server to (default: {DEFAULT_HOST})')
@click.option('--port', default=DEFAULT_PORT, type=int,
              help=f'Port to bind the server to (default: {DEFAULT_PORT})')
@click.option('--mongodb-url', default=None,
              help='MongoDB connection URL')
@click.option('--mongodb-db', default=None,
              help='MongoDB database name')
@click.version_option(version='0.1.0')
def cli(ctx, transport, host, port, mongodb_url, mongodb_db):
    """MongoDB MCP Server - A MongoDB interface for AI agents using MCP protocol."""
    if ctx.invoked_subcommand is None:
        # 환경 변수 설정
        if mongodb_url:
            os.environ["MONGODB_URL"] = mongodb_url
        elif "MONGODB_URL" not in os.environ:
            os.environ["MONGODB_URL"] = DEFAULT_MONGODB_URL
            click.echo(f"Warning: Using default MongoDB URL: {DEFAULT_MONGODB_URL}")
        
        if mongodb_db:
            os.environ["MONGODB_DB"] = mongodb_db
            
        # 로그 출력
        click.echo(f"Starting MongoDB MCP Server with {transport} transport")
        click.echo(f"Server running at: http://{host}:{port}")
        click.echo(f"MCP Endpoint: http://{host}:{port}/mcp")
        click.echo(f"Health Check: http://{host}:{port}/health")
        
        # SSE 모드에 따른 추가 메시지
        if transport == 'sse':
            click.echo(f"SSE Endpoint: http://{host}:{port}/sse")
            os.environ["MCP_TRANSPORT"] = "sse"
        else:
            os.environ["MCP_TRANSPORT"] = "http"
        
        # 서버 시작
        uvicorn.run("app.main:app", host=host, port=port, log_level="info")

@cli.command()
def info():
    """Display information about the MongoDB MCP Server."""
    click.echo("MongoDB MCP Server - Version 0.1.0")
    click.echo("A MongoDB interface for AI agents using Model Context Protocol")
    click.echo("\nSupported transports:")
    click.echo("  - HTTP (default)")
    click.echo("  - SSE (Server-Sent Events)")
    click.echo("\nAvailable tools:")
    click.echo("  - listCollections: List all collections in a database")
    click.echo("  - find: Query documents in a collection")
    click.echo("  - insertOne: Insert a single document into a collection")
    click.echo("  - updateOne: Update a single document in a collection")
    click.echo("  - deleteOne: Delete a single document from a collection")
    click.echo("  - indexes: List all indexes for a collection")
    click.echo("  - createIndex: Create a new index on a collection")
    click.echo("  - dropIndex: Drop an existing index from a collection")
    click.echo("\nUsage with UVX:")
    click.echo("  uvx mongo-mcp-server")
    click.echo("  uvx mongo-mcp-server --transport=sse")

def main():
    """Entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
