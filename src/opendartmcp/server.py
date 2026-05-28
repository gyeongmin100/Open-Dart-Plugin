import argparse
import asyncio
import getpass
import sys
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP
from opendartmcp.client import DartClient
from opendartmcp.config import clear_api_key, get_config_path, mask_api_key, resolve_api_key, save_api_key
from opendartmcp.errors import DartApiError
from opendartmcp.tools import (
    disclosure,
    business_report,
    financial,
    stock_holdings,
    major_report,
    securities,
)


def create_server() -> FastMCP:
    resolved = resolve_api_key()
    if not resolved:
        raise RuntimeError(
            "OpenDART API key is not configured. Run "
            "`opendartmcp config set-api-key` or set DART_API_KEY."
        )

    client = DartClient(resolved.api_key)

    @asynccontextmanager
    async def lifespan(server):
        try:
            yield
        finally:
            await client.aclose()

    mcp = FastMCP("open-dart", lifespan=lifespan)

    disclosure.register(mcp, client)
    business_report.register(mcp, client)
    financial.register(mcp, client)
    stock_holdings.register(mcp, client)
    major_report.register(mcp, client)
    securities.register(mcp, client)

    return mcp


async def validate_api_key(api_key: str) -> tuple[bool, str]:
    client = DartClient(api_key)
    try:
        await client.get_json("/company.json", {"corp_code": "00126380"})
    except DartApiError as error:
        return False, f"{error.status}: {error.message}"
    except Exception as error:
        return False, str(error)
    finally:
        await client.aclose()

    return True, "OpenDART API key is valid."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="opendartmcp")
    subparsers = parser.add_subparsers(dest="command")

    config_parser = subparsers.add_parser("config", help="Manage OpenDART API key configuration")
    config_subparsers = config_parser.add_subparsers(dest="config_command", required=True)
    config_subparsers.add_parser("set-api-key", help="Save an OpenDART API key")
    config_subparsers.add_parser("show", help="Show current API key configuration")
    config_subparsers.add_parser("test", help="Validate the configured API key with OpenDART")
    config_subparsers.add_parser("clear-api-key", help="Remove the saved OpenDART API key")

    return parser


def handle_config_command(args: argparse.Namespace) -> int:
    if args.config_command == "set-api-key":
        api_key = getpass.getpass("OpenDART API key: ").strip()
        if not api_key:
            print("API key was not saved because the input was empty.", file=sys.stderr)
            return 1
        save_api_key(api_key)
        print(f"API key saved to: {get_config_path()}")
        return 0

    if args.config_command == "show":
        resolved = resolve_api_key()
        if not resolved:
            print("API Key: not configured")
            print(f"Config: {get_config_path()}")
            print("Run: opendartmcp config set-api-key")
            return 1

        print(f"API Key: {mask_api_key(resolved.api_key)}")
        print(f"Source: {resolved.source}")
        print(f"Config: {resolved.config_path or get_config_path()}")
        return 0

    if args.config_command == "test":
        resolved = resolve_api_key()
        if not resolved:
            print("API key is not configured. Run: opendartmcp config set-api-key", file=sys.stderr)
            return 1

        ok, message = asyncio.run(validate_api_key(resolved.api_key))
        print(message)
        return 0 if ok else 1

    if args.config_command == "clear-api-key":
        removed = clear_api_key()
        if removed:
            print(f"API key removed from: {get_config_path()}")
        else:
            print("No saved API key was found.")
        return 0

    raise RuntimeError(f"Unknown config command: {args.config_command}")


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if argv:
        parser = build_parser()
        args = parser.parse_args(argv)
        if args.command == "config":
            return handle_config_command(args)

    mcp = create_server()
    mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
