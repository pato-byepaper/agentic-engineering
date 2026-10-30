#!/usr/bin/env python3
"""
mcp_server.py - Advanced Model Context Protocol (MCP) server for AGY Gemini models.
Exposes custom tools for token-efficient Markdown RAG (headings, diagrams, code blocks, alerts, tables)
and Dependency Relationship Graphs (with predefined dangerous operations, test links, and blast radius checking).
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
    extract_acceptance_criteria,
    extract_agent_assignments,
    extract_alerts,
    extract_code_blocks,
    extract_diagrams,
    extract_endpoints,
    extract_env_vars,
    extract_frontmatter,
    extract_from_rag,
    extract_tables,
    extract_tasks,
    get_topics,
    save_in_rag,
    search_rag,
)
from graph_service import (
    DEFAULT_GRAPH_JSON,
    PREDEFINED_RELATIONSHIPS,
    add_relationship,
    check_impact,
    export_mermaid,
    get_relationships,
    list_entities,
    list_relationship_types,
    load_graph,
)

SERVER_NAME = "context-services-mcp"
SERVER_VERSION = "2.0.0"

TOOLS_DEFINITIONS = [
    # RAG Tools
    {
        "name": "get_topics",
        "description": "Scans a markdown file using regex to extract hierarchical topics (# through ######) with line boundaries and line counts. Use this first before reading large context files to maintain minimal token usage.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the markdown context file (defaults to .agents/context/knowledge_base.md)"
                },
                "depth": {
                    "type": "integer",
                    "description": "Max heading depth to inspect (defaults to 4)"
                }
            }
        }
    },
    {
        "name": "extract_from_rag",
        "description": "Extracts ONLY the in-between lines for a specific topic (#), subtopic (##), or section (###) using regex boundaries. Minimizes token consumption when reading large documents.",
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
                "section": {
                    "type": "string",
                    "description": "Optional deep section title (### or deeper)"
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
        "name": "extract_diagrams",
        "description": "Extracts all Mermaid diagrams (flowcharts, sequence diagrams, ERDs) from markdown without loading surrounding prose.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Optional topic name to limit extraction to a specific section"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the markdown file"
                }
            }
        }
    },
    {
        "name": "extract_code_blocks",
        "description": "Extracts fenced code blocks filtered by programming language (sql, ts, py, bash, json) from markdown.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "language": {
                    "type": "string",
                    "description": "Optional language tag filter (e.g. sql, typescript, python, bash, json)"
                },
                "topic": {
                    "type": "string",
                    "description": "Optional topic name to limit extraction"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the markdown file"
                }
            }
        }
    },
    {
        "name": "extract_alerts",
        "description": "Extracts critical callouts and safety invariants (> [!WARNING], > [!DANGER], > [!IMPORTANT], > [!CAUTION]). Use this to check safety guidelines before executing tasks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Optional alert type filter (WARNING, DANGER, IMPORTANT, NOTE, CAUTION)"
                },
                "topic": {
                    "type": "string",
                    "description": "Optional topic name"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the markdown file"
                }
            }
        }
    },
    {
        "name": "extract_tables",
        "description": "Extracts and parses markdown data tables into structured columns and rows.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Optional topic name"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the markdown file"
                }
            }
        }
    },
    {
        "name": "search_rag",
        "description": "Searches for a keyword or regex pattern in the markdown file and returns ONLY the enclosing section (heading + in-between lines), without loading irrelevant document parts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keyword or regular expression"
                },
                "regex": {
                    "type": "boolean",
                    "description": "Whether to treat query as regex (default: false)"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the markdown file"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "extract_agent_assignments",
        "description": "Extracts sections, tasks, and instruction blocks assigned to sub-agents via '@agent-name' or 'sub-agent-in-charge: <agent>'. Allows sub-agents (backend-developer, tester, data-engineer) to isolate their exact work items from large documents without reading the rest.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent": {
                    "type": "string",
                    "description": "Agent name to filter by (e.g. backend-developer, tester, data-engineer, tech-lead)"
                },
                "topic": {
                    "type": "string",
                    "description": "Optional topic filter"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the markdown file (defaults to knowledge base)"
                }
            }
        }
    },
    {
        "name": "extract_tasks",
        "description": "Extracts markdown checklist items (- [ ] pending, - [x] completed) across sections, optionally filtered by status ('all', 'pending', 'completed') and assigned agent.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["all", "pending", "completed"],
                    "description": "Task status filter (default: 'all')"
                },
                "agent": {
                    "type": "string",
                    "description": "Filter tasks assigned to specific agent (e.g. backend-developer)"
                },
                "topic": {
                    "type": "string",
                    "description": "Optional topic filter"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the markdown file"
                }
            }
        }
    },
    {
        "name": "extract_acceptance_criteria",
        "description": "Extracts sections containing Acceptance Criteria, Definition of Done, Invariants, or Non-Negotiable Rules from tickets and plans.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Optional topic filter"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the markdown file"
                }
            }
        }
    },
    {
        "name": "extract_endpoints",
        "description": "Extracts HTTP API routes (GET, POST, PUT, DELETE, PATCH /...) defined in markdown specifications with enclosing section context.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Optional topic filter"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the markdown file"
                }
            }
        }
    },
    {
        "name": "extract_env_vars",
        "description": "Extracts environment variables and configuration keys (e.g. DATABASE_URL, PORT) from markdown documents.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Optional topic filter"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the markdown file"
                }
            }
        }
    },
    {
        "name": "extract_frontmatter",
        "description": "Extracts YAML/JSON frontmatter from the header of markdown documents (--- ... ---).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the markdown file"
                }
            }
        }
    },
    {
        "name": "save_in_rag",
        "description": "Saves or appends notes, architectural invariants, or large context under a # topic, ## subtopic, or ### section in the markdown RAG file.",
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
                "section": {
                    "type": "string",
                    "description": "Optional deep section title (###)"
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

    # Graph Tools
    {
        "name": "add_relationship",
        "description": "Records an architectural or dependency relationship between two entities and updates the live Mermaid diagram. Supports predefined dangerous operations (dangerously_destroys, dangerously_breaks, dangerously_overwrites, dangerously_exposes), testing links (tests, unit_tests, e2e_tests, mocks), architecture (depends_on, calls, implements, queries), and custom relations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "Source entity or component name"
                },
                "relationship": {
                    "type": "string",
                    "description": "Relationship type (e.g. dangerously_destroys, dangerously_breaks, tests, depends_on, calls, implements, queries, blocks)"
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
        "description": "Queries the dependency graph for an entity's incoming, outgoing, or all connections. Can filter by danger flag or category.",
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
                "category": {
                    "type": "string",
                    "enum": ["danger", "testing", "architecture", "coordination"],
                    "description": "Filter by predefined category"
                },
                "only_dangerous": {
                    "type": "boolean",
                    "description": "If true, only return dangerous relationships"
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
        "name": "check_impact",
        "description": "Pre-edit blast radius analysis! Evaluates associated test files, downstream consumers that might break, and dangerous relationships connected to an entity/file before making changes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity": {
                    "type": "string",
                    "description": "Entity, component, or file path to evaluate before editing"
                },
                "file_path": {
                    "type": "string",
                    "description": "Custom graph storage JSON path"
                }
            },
            "required": ["entity"]
        }
    },
    {
        "name": "list_relationship_types",
        "description": "Lists all predefined relationship types (including dangerous operations and test links) and their descriptions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": [
                        "danger",
                        "testing",
                        "data",
                        "contract",
                        "ui_state",
                        "infrastructure",
                        "architecture",
                        "governance",
                        "coordination"
                    ],
                    "description": "Optional category filter: danger, testing, data, contract, ui_state, infrastructure, architecture, governance, coordination"
                }
            }
        }
    },
    {
        "name": "export_graph_mermaid",
        "description": "Exports the complete dependency and relationship graph as a Mermaid flowchart diagram with danger alerts.",
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
    payload = json.dumps(response)
    sys.stdout.write(payload + "\n")
    sys.stdout.flush()


def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if name == "get_topics":
            file_path = Path(arguments.get("file_path", DEFAULT_RAG_FILE))
            depth = arguments.get("depth", 4)
            res = get_topics(file_path, depth)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "extract_from_rag":
            topic = arguments["topic"]
            subtopic = arguments.get("subtopic")
            section = arguments.get("section")
            file_path = Path(arguments.get("file_path", DEFAULT_RAG_FILE))
            res = extract_from_rag(topic, subtopic, section, file_path)
            if "error" in res and res["error"]:
                return {"isError": True, "content": [{"type": "text", "text": res["error"]}]}
            return {"content": [{"type": "text", "text": res["content"]}]}

        elif name == "extract_diagrams":
            topic = arguments.get("topic")
            file_path = Path(arguments.get("file_path", DEFAULT_RAG_FILE))
            res = extract_diagrams(topic, file_path)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "extract_code_blocks":
            language = arguments.get("language")
            topic = arguments.get("topic")
            file_path = Path(arguments.get("file_path", DEFAULT_RAG_FILE))
            res = extract_code_blocks(language, topic, file_path)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "extract_alerts":
            atype = arguments.get("type")
            topic = arguments.get("topic")
            file_path = Path(arguments.get("file_path", DEFAULT_RAG_FILE))
            res = extract_alerts(atype, topic, file_path)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "extract_tables":
            topic = arguments.get("topic")
            file_path = Path(arguments.get("file_path", DEFAULT_RAG_FILE))
            res = extract_tables(topic, file_path)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "extract_agent_assignments":
            agent = arguments.get("agent")
            topic = arguments.get("topic")
            file_path = Path(arguments.get("file_path", DEFAULT_RAG_FILE))
            res = extract_agent_assignments(agent, topic, file_path)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "extract_tasks":
            status = arguments.get("status", "all")
            agent = arguments.get("agent")
            topic = arguments.get("topic")
            file_path = Path(arguments.get("file_path", DEFAULT_RAG_FILE))
            res = extract_tasks(status, agent, topic, file_path)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "extract_acceptance_criteria":
            topic = arguments.get("topic")
            file_path = Path(arguments.get("file_path", DEFAULT_RAG_FILE))
            res = extract_acceptance_criteria(topic, file_path)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "extract_endpoints":
            topic = arguments.get("topic")
            file_path = Path(arguments.get("file_path", DEFAULT_RAG_FILE))
            res = extract_endpoints(topic, file_path)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "extract_env_vars":
            topic = arguments.get("topic")
            file_path = Path(arguments.get("file_path", DEFAULT_RAG_FILE))
            res = extract_env_vars(topic, file_path)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "extract_frontmatter":
            file_path = Path(arguments.get("file_path", DEFAULT_RAG_FILE))
            res = extract_frontmatter(file_path)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "search_rag":
            query = arguments["query"]
            regex = arguments.get("regex", False)
            file_path = Path(arguments.get("file_path", DEFAULT_RAG_FILE))
            res = search_rag(query, regex, False, file_path)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "save_in_rag":
            topic = arguments["topic"]
            content = arguments["content"]
            subtopic = arguments.get("subtopic")
            section = arguments.get("section")
            mode = arguments.get("mode", "append")
            file_path = Path(arguments.get("file_path", DEFAULT_RAG_FILE))
            res = save_in_rag(topic, content, subtopic, section, file_path, mode)
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
            category = arguments.get("category")
            only_dangerous = arguments.get("only_dangerous", False)
            file_path = Path(arguments.get("file_path", DEFAULT_GRAPH_JSON))
            res = get_relationships(entity, relationship, direction, category, only_dangerous, file_path)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "check_impact":
            entity = arguments["entity"]
            file_path = Path(arguments.get("file_path", DEFAULT_GRAPH_JSON))
            res = check_impact(entity, file_path)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "list_relationship_types":
            category = arguments.get("category")
            res = list_relationship_types(category)
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
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        if line.lower().startswith("content-length:"):
            try:
                length = int(line.split(":")[1].strip())
                sys.stdin.readline()
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

        if method == "initialize":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION}
                }
            })
        elif method == "notifications/initialized":
            pass
        elif method == "tools/list":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": TOOLS_DEFINITIONS}
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
            send_response({"jsonrpc": "2.0", "id": req_id, "result": {}})
        else:
            if req_id is not None:
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                })


if __name__ == "__main__":
    run_stdio_server()
