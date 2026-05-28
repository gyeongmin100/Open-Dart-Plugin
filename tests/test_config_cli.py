import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from opendartmcp import server


class ConfigCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.config_file = Path(self.tempdir.name) / "config.json"

    def test_saved_api_key_is_loaded_when_environment_is_absent(self) -> None:
        with patch.dict(os.environ, {"OPENDARTMCP_CONFIG_FILE": str(self.config_file)}, clear=True):
            from opendartmcp.config import load_config, resolve_api_key, save_api_key

            save_api_key("test-key")

            self.assertEqual(load_config()["dart_api_key"], "test-key")
            self.assertEqual(resolve_api_key().api_key, "test-key")
            self.assertEqual(resolve_api_key().source, "user config")

    def test_environment_api_key_takes_precedence_over_saved_config(self) -> None:
        with patch.dict(
            os.environ,
            {
                "DART_API_KEY": "env-key",
                "OPENDARTMCP_CONFIG_FILE": str(self.config_file),
            },
            clear=True,
        ):
            from opendartmcp.config import resolve_api_key, save_api_key

            save_api_key("saved-key")

            resolved = resolve_api_key()
            self.assertEqual(resolved.api_key, "env-key")
            self.assertEqual(resolved.source, "environment")

    def test_mask_api_key_does_not_expose_full_value(self) -> None:
        from opendartmcp.config import mask_api_key

        masked = mask_api_key("abcd12345678wxyz")

        self.assertEqual(masked, "abcd********wxyz")
        self.assertNotIn("12345678", masked)

    def test_clear_api_key_removes_saved_value(self) -> None:
        with patch.dict(os.environ, {"OPENDARTMCP_CONFIG_FILE": str(self.config_file)}, clear=True):
            from opendartmcp.config import clear_api_key, load_config, save_api_key

            save_api_key("test-key")
            clear_api_key()

            self.assertNotIn("dart_api_key", load_config())

    def test_missing_api_key_error_mentions_cli_setup_command(self) -> None:
        with patch.dict(os.environ, {"OPENDARTMCP_CONFIG_FILE": str(self.config_file)}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "opendartmcp config set-api-key"):
                server.create_server()

    def test_config_show_masks_api_key(self) -> None:
        with patch.dict(os.environ, {"OPENDARTMCP_CONFIG_FILE": str(self.config_file)}, clear=True):
            from opendartmcp.config import save_api_key

            save_api_key("abcd12345678wxyz")

            with patch("builtins.print") as print_mock:
                exit_code = server.main(["config", "show"])

            output = "\n".join(str(call.args[0]) for call in print_mock.call_args_list)
            self.assertEqual(exit_code, 0)
            self.assertIn("abcd********wxyz", output)
            self.assertNotIn("abcd12345678wxyz", output)

    def test_set_api_key_command_saves_prompted_value(self) -> None:
        with patch.dict(os.environ, {"OPENDARTMCP_CONFIG_FILE": str(self.config_file)}, clear=True):
            with patch("getpass.getpass", return_value="prompted-key"):
                with patch("builtins.print"):
                    exit_code = server.main(["config", "set-api-key"])

            from opendartmcp.config import load_config

            self.assertEqual(exit_code, 0)
            self.assertEqual(load_config()["dart_api_key"], "prompted-key")

    def test_config_test_uses_configured_api_key_without_network_in_unit_test(self) -> None:
        async def fake_validate(api_key: str) -> tuple[bool, str]:
            return api_key == "saved-key", "validated"

        with patch.dict(os.environ, {"OPENDARTMCP_CONFIG_FILE": str(self.config_file)}, clear=True):
            from opendartmcp.config import save_api_key

            save_api_key("saved-key")
            with patch("opendartmcp.server.validate_api_key", fake_validate):
                with patch("builtins.print") as print_mock:
                    exit_code = server.main(["config", "test"])

            output = "\n".join(str(call.args[0]) for call in print_mock.call_args_list)
            self.assertEqual(exit_code, 0)
            self.assertIn("validated", output)


if __name__ == "__main__":
    unittest.main()
