import os
from mcp.server.fastmcp import FastMCP
from opendartmcp.client import DartClient
from opendartmcp.tools import disclosure, financial, stock_holdings, business_report


def create_server() -> FastMCP:
    api_key = os.environ.get("DART_API_KEY")
    if not api_key:
        raise RuntimeError("DART_API_KEY 환경변수가 설정되지 않았습니다")

    client = DartClient(api_key)
    mcp = FastMCP("open-dart")

    disclosure.register(mcp, client)
    financial.register(mcp, client)
    stock_holdings.register(mcp, client)
    business_report.register(mcp, client)

    return mcp


def main():
    mcp = create_server()
    mcp.run()


if __name__ == "__main__":
    main()
