import unittest
from unittest.mock import patch, MagicMock
from badfish.main import main


class TestAsyncioFix(unittest.TestCase):
    @patch("badfish.main.execute_badfish")
    @patch("badfish.main.BadfishLogger")
    @patch("badfish.main.parse_arguments")
    @patch("asyncio.set_event_loop")
    @patch("asyncio.new_event_loop")
    @patch("asyncio.get_event_loop")
    def test_main_handles_no_event_loop(
        self, mock_get_loop, mock_new_loop, mock_set_loop, mock_parse_args, mock_logger, mock_execute
    ):
        mock_get_loop.side_effect = RuntimeError("No event loop")

        mock_loop_instance = MagicMock()
        mock_new_loop.return_value = mock_loop_instance
        mock_loop_instance.run_until_complete.return_value = ("localhost", True)

        mock_parse_args.return_value = {
            "verbose": False,
            "host": "localhost",
            "delta": None,
            "firmware_inventory": None,
            "host_list": None,
            "log": None,
            "output": None,
        }

        main()

        mock_get_loop.assert_called_once()
        mock_new_loop.assert_called_once()
        mock_set_loop.assert_called_once_with(mock_loop_instance)
        mock_loop_instance.run_until_complete.assert_called()

    @patch("badfish.main.execute_badfish")
    @patch("badfish.main.BadfishLogger")
    @patch("badfish.main.parse_arguments")
    @patch("asyncio.set_event_loop")
    @patch("asyncio.new_event_loop")
    @patch("asyncio.get_event_loop")
    def test_main_uses_existing_loop(
        self, mock_get_loop, mock_new_loop, mock_set_loop, mock_parse_args, mock_logger, mock_execute
    ):
        existing_loop = MagicMock()
        mock_get_loop.return_value = existing_loop
        mock_get_loop.side_effect = None
        existing_loop.run_until_complete.return_value = ("localhost", True)

        mock_parse_args.return_value = {
            "verbose": False,
            "host": "localhost",
            "delta": None,
            "firmware_inventory": None,
            "host_list": None,
            "log": None,
            "output": None,
        }

        main()

        mock_get_loop.assert_called_once()
        mock_new_loop.assert_not_called()
        mock_set_loop.assert_not_called()
        existing_loop.run_until_complete.assert_called()
