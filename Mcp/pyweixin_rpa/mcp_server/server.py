from fastmcp import FastMCP
from mcp_server.tools.messaging import mcp as messaging_mcp
mcp=FastMCP("pyweixin_rpa")

# 挂载子模块
mcp.mount(messaging_mcp)

if __name__ == "__main__":
    mcp.run()