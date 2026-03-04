import asyncio
import os
import sys

# Ensure parent is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.core import OpenClawMCP

async def main_loop():
    print("=================================================")
    print("Welcome to Open Claw (MCP Edition) CLI")
    print("Type 'exit' or 'quit' to close.")
    print("=================================================")
    
    agent = OpenClawMCP()
    
    # Locate configuration file 
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_config.json")
    if not os.path.exists(config_path):
        print(f"Failed to find {config_path}. Did you run ./auto_deploy.sh?")
        return

    # Connect to MCP servers specified in config
    await agent.connect_to_servers(config_path)

    try:
        while True:
            # We use a simple thread executor for input() to avoid blocking the async event loop, 
            # though for a simple CLI a blocking input is usually fine if no background tasks are running.
            user_input = await asyncio.to_thread(input, "\nYou: ")
            
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            if not user_input.strip():
                continue
            
            response = await agent.chat(user_input)
            print(f"\nOpen Claw:\n{response}")
    except KeyboardInterrupt:
         print("\nGoodbye!")
    except Exception as e:
         print(f"\nFatal error: {e}")
    finally:
         await agent.close()

def main():
    asyncio.run(main_loop())

if __name__ == "__main__":
    main()
