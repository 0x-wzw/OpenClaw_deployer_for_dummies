import asyncio
import json
import traceback
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Import config
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME

class OpenClawMCP:
    def __init__(self):
        self.openai = AsyncOpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL if "api.openai.com" not in OPENAI_BASE_URL else None
        )
        self.model = MODEL_NAME
        self.messages = [
            {"role": "system", "content": "You are Open Claw, a highly advanced local AI agent connected to external tools via Model Context Protocol (MCP). Use your tools as needed to help the user. If you encounter errors, relay them and try alternative methods."}
        ]
        self.sessions: Dict[str, ClientSession] = {}
        self.tool_to_server: Dict[str, str] = {}
        self.openai_tools: List[Dict] = []
        self.exit_stack = AsyncExitStack()

    async def connect_to_servers(self, config_path: str):
        """Reads mcp_config.json and establishes Stdio connections to all defined servers."""
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error reading {config_path}: {e}")
            return
            
        for server_name, server_config in config.get("mcpServers", {}).items():
            print(f"[Core] Connecting to MCP server: {server_name}...")
            try:
                server_params = StdioServerParameters(
                    command=server_config["command"],
                    args=server_config["args"],
                    env=None # Inherit from parent
                )
                
                stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
                read, write = stdio_transport
                session = await self.exit_stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                
                self.sessions[server_name] = session
                
                # Retrieve and cache tool definitions
                tools_response = await session.list_tools()
                for tool in tools_response.tools:
                    self.tool_to_server[tool.name] = server_name
                    # Convert MCP tool schema directly to OpenAI tool schema
                    self.openai_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema
                        }
                    })
                print(f"[Core] Connected to {server_name}. Loaded {len(tools_response.tools)} tools.")
            except Exception as e:
                print(f"[Core] Failed to connect to {server_name}: {e}")

    async def chat(self, user_input: str) -> str:
        """Sends user input to the agent and handles the tool execution loop."""
        self.messages.append({"role": "user", "content": user_input})
        
        while True:
            # 1. Call the model
            try:
                response = await self.openai.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=self.openai_tools if self.openai_tools else None,
                    tool_choice="auto" if self.openai_tools else None,
                )
            except Exception as e:
                return f"Error communicating with LLM API: {e}"

            response_message = response.choices[0].message
            tool_calls = getattr(response_message, 'tool_calls', None)
            
            # Append completion to history
            if response_message.content:
                self.messages.append({"role": "assistant", "content": response_message.content, "tool_calls": tool_calls})
            else:
                 self.messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls})

            # 2. Check for tool calls
            if tool_calls:
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    server_name = self.tool_to_server.get(function_name)
                    
                    if not server_name:
                         print(f"Warning: Model hallucinated a function {function_name}")
                         self.messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": f"Error: Tool {function_name} not found.",
                         })
                         continue
                    
                    session = self.sessions[server_name]
                    try:
                        function_args = json.loads(tool_call.function.arguments)
                        print(f"\n[Open Claw calling MCP Tool: {function_name} via {server_name}]")
                        
                        # Call MCP Tool
                        result = await session.call_tool(function_name, arguments=function_args)
                        
                        # Standard MCP tools return content as a list of Content objects (TextContent, ImageContent)
                        output_texts = []
                        if result.isError:
                             output_texts.append(f"Tool Error: {result.content}")
                        else:
                             for content in result.content:
                                  if content.type == "text":
                                       output_texts.append(content.text)
                                  else:
                                       output_texts.append(f"[{content.type} output omitted]")
                        
                        final_output = "\n".join(output_texts)
                        if not final_output:
                             final_output = "Tool executed successfully but returned no text."

                        self.messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": final_output,
                            }
                        )
                    except Exception as e:
                         print(f"\n[Error executing {function_name}: {e}]")
                         self.messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": f"Execution error: {str(e)}",
                            }
                        )
                # Loop continues
            else:
                # 3. Final text answer
                return response_message.content if response_message.content else "Done"

    async def close(self):
        await self.exit_stack.aclose()
