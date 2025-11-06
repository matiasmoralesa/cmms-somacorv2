import unittest
from unittest.mock import patch, MagicMock
from notification_services.factory import get_notification_service
from notification_services.telegram_service import TelegramNotificationService

class TestNotificationFactory(unittest.TestCase):

    def test_get_telegram_service(self):
        with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "test_token"}):
            service = get_notification_service("telegram")
            self.assertIsInstance(service, TelegramNotificationService)

    def test_get_invalid_service(self):
        with self.assertRaises(ValueError):
            get_notification_service("invalid_service")

class TestTelegramService(unittest.TestCase):

    @patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "test_token"})
    @patch("telegram.Bot")
    async def test_send_message(self, MockBot):
        mock_bot_instance = MockBot.return_value
        mock_bot_instance.send_message = MagicMock()

        service = TelegramNotificationService()
        await service.send_message("test_chat_id", "test_message")

        mock_bot_instance.send_message.assert_called_once_with(chat_id="test_chat_id", text="test_message")

if __name__ == "__main__":
    unittest.main()

