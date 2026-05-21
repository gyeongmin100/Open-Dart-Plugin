import os
from mcp.server.fastmcp import FastMCP
from opendartmcp.client import DartClient


def create_server() -> FastMCP:
    api_key = os.environ.get("DART_API_KEY")
    if not api_key:
        raise RuntimeError("DART_API_KEY 환경변수가 설정되지 않았습니다")

    client = DartClient(api_key)
    mcp = FastMCP("open-dart")

    # TODO: 각 툴 모듈 register 호출 (추후 단계에서 추가)

    return mcp


def main():
    mcp = create_server()
    mcp.run()


if __name__ == "__main__":
    main()
