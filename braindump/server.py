#jai siya ram
#only file that host / VOICEOS would every talk to 
from mcp.server.mcpserver import MCPServer
server = MCPServer("notes-manager")

@server.tool()
def ping()->str:
    """check if the server is working or not , use when the user says ping"""
    return "pong"

if __name__ == "__main__":
    server.run()