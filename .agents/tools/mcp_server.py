#!/usr/bin/env python3
"""
mcp_server.py - Zero-dependency Model Context Protocol (MCP) server for AGY Gemini models.
Exposes custom tools for token-efficient Markdown RAG and Dependency Relationship Graphs over stdio.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import local service functions
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from rag_service import (
    DEFAULT_RAG_FILE,
    extract_from_rag,
    get_topics,
    save_in_rag,
)
from graph_service import (
    DEFAULT_GRAPH_JSON,
    add_relationship,
    export_mermaid,
    get_relationships,
    list_entities,
    load_graph,
)

SERVER_NAME = "context-services-mcp"
SERVER_VERSION = "1.0.0"

TOOLS_DEFINITIONS = [
    {
        "name": "get_topics",
        "description": "Scans a markdown file using regex to extract all topics (#) and subtopics (##) with their line boundaries and counts. Use this first before reading large context files to maintain minimal token usage.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the markdown context file (defaults to .agents/context/knowledge_base.md)"
                }
            }
        }
    },
    {
        "name": "extract_from_rag",
        "description": "Extracts ONLY the in-between lines for a specific topic (#) or subtopic (##) using regex boundaries. Minimizes token consumption when inspecting large context.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Main topic title (#)"
                },
                "subtopic": {
                    "type": "string",
                    "description": "Optional subtopic title (##)"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the markdown context file"
                }
            },
            "required": ["topic"]
        }
    },
    {
        "name": "save_in_rag",
        "description": "Saves or appends notes, architectural invariants, or large context under a # topic or ## subtopic in the markdown RAG file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Main topic title (#)"
                },
                "content": {
                    "type": "string",
                    "description": "Markdown content to persist"
                },
                "subtopic": {
                    "type": "string",
                    "description": "Optional subtopic title (##)"
                },
                "mode": {
                    "type": "string",
                    "enum": ["append", "replace"],
                    "description": "Whether to append to or replace existing section (defaults to append)"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the markdown context file"
                }
            },
            "required": ["topic", "content"]
        }
    },
    {
        "name": "add_relationship",
        "description": "Records an architectural or dependency relationship between two entities (e.g. ServiceA depends_on ServiceB, Controller calls Service) and updates the live Mermaid diagram.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "Source entity or component name"
                },
                "relationship": {
                    "type": "string",
                    "description": "Relationship type (e.g. depends_on, calls, implements, migrates_to, blocks, imports)"
                },
                "target": {
                    "type": "string",
                    "description": "Target entity or component name"
                },
                "metadata": {
                    "type": "object",
                    "description": "Optional key-value metadata (notes, layer, protocol)"
                },
                "file_path": {
                    "type": "string",
                    "description": "Custom graph storage JSON path"
                }
            },
            "required": ["source", "relationship", "target"]
        }
    },
    {
        "name": "get_relationships",
        "description": "Queries the dependency graph for an entity's incoming, outgoing, or all connections.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity": {
                    "type": "string",
                    "description": "Optional entity name to query"
                },
                "relationship": {
                    "type": "string",
                    "description": "Optional relationship type filter"
                },
                "direction": {
                    "type": "string",
                    "enum": ["all", "outgoing", "incoming"],
                    "description": "Direction relative to entity (defaults to all)"
                },
                "file_path": {
                    "type": "string",
                    "description": "Custom graph storage JSON path"
                }
            }
        }
    },
    {
        "name": "export_graph_mermaid",
        "description": "Exports the complete dependency and relationship graph as a Mermaid flowchart diagram.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "orientation": {
                    "type": "string",
                    "enum": ["TD", "LR"],
                    "description": "Flowchart orientation (Top-Down or Left-to-Right)"
                },
                "file_path": {
                    "type": "string",
                    "description": "Custom graph storage JSON path"
                }
            }
        }
    }
]


def send_response(response: Dict[str, Any]):
    """Sends a JSON-RPC response over standard output with newline delimiter."""
    payload = json.dumps(response)
    # Output line-delimited JSON
    sys.stdout.write(payload + "\n")
    sys.stdout.flush()


def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatches tool execution to the appropriate service."""
    try:
        if name == "get_topics":
            file_path = Path(arguments.get("file_path", DEFAULT_RAG_FILE))
            res = get_topics(file_path)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "extract_from_rag":
            topic = arguments["topic"]
            subtopic = arguments.get("subtopic")
            file_path = Path(arguments.get("file_path", DEFAULT_RAG_FILE))
            res = extract_from_rag(topic, subtopic, file_path)
            if "error" in res and res["error"]:
                return {"isError": True, "content": [{"type": "text", "text": res["error"]}]}
            return {"content": [{"type": "text", "text": res["content"]}]}

        elif name == "save_in_rag":
            topic = arguments["topic"]
            content = arguments["content"]
            subtopic = arguments.get("subtopic")
            mode = arguments.get("mode", "append")
            file_path = Path(arguments.get("file_path", DEFAULT_RAG_FILE))
            res = save_in_rag(topic, content, subtopic, file_path, mode)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "add_relationship":
            source = arguments["source"]
            relationship = arguments["relationship"]
            target = arguments["target"]
            metadata = arguments.get("metadata")
            file_path = Path(arguments.get("file_path", DEFAULT_GRAPH_JSON))
            res = add_relationship(source, relationship, target, metadata, file_path)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "get_relationships":
            entity = arguments.get("entity")
            relationship = arguments.get("relationship")
            direction = arguments.get("direction", "all")
            file_path = Path(arguments.get("file_path", DEFAULT_GRAPH_JSON))
            res = get_relationships(entity, relationship, direction, file_path)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "export_graph_mermaid":
            orientation = arguments.get("orientation", "TD")
            file_path = Path(arguments.get("file_path", DEFAULT_GRAPH_JSON))
            data = load_graph(file_path)
            mmd = export_mermaid(data, file_path.with_suffix(".mmd"), orientation)
            return {"content": [{"type": "text", "text": mmd}]}

        else:
            return {"isError": True, "content": [{"type": "text", "text": f"Unknown tool: {name}"}]}

    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": f"Error executing {name}: {str(e)}"}]}


def run_stdio_server():
    """Main loop reading JSON-RPC requests from standard input."""
    # Ensure unbuffered text IO
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        # Check for Content-Length header prefix if LSP framing is used
        if line.lower().startswith("content-length:"):
            try:
                length = int(line.split(":")[1].strip())
                # Read empty separator line
                sys.stdin.readline()
                # Read content bytes
                content = sys.stdin.read(length)
                request = json.loads(content)
            except Exception as e:
                sys.stderr.write(f"Framing error: {e}\n")
                continue
        else:
            try:
                request = json.loads(line)
            except Exception:
                continue

        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Handle MCP methods
        if method == "initialize":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "version": SERVER_VERSION
                    }
                }
            })
        elif method == "notifications/initialized":
            # No response needed for notification
            pass
        elif method == "tools/list":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": TOOLS_DEFINITIONS
                }
            })
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            result = handle_tool_call(tool_name, tool_args)
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result
            })
        elif method == "ping":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {}
            })
        else:
            if req_id is not None:
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                })


if __name__ == "__main__":
    run_stdio_server()
