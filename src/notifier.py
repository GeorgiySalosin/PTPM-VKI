from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class Notifier(ABC):
    """
    Абстрактный интерфейс сторонней зависимости.
    """

    @abstractmethod
    def send(self, message: str) -> bool:
        """
        Передать строку-результат стороннему процессу.

        :param message: строка для отправки.
        :return: True, если передача «успешна», False — если нет.
        """
        ...

    @abstractmethod
    def get_sent_messages(self) -> list[str]:
        """Вернуть список уже отправленных сообщений (для проверки/отладки)."""
        ...


class EmailNotifier(Notifier):
    """
    Имитация отправки email.
    """

    def __init__(self, recipient: str, sender: str = "noreply@triangle.local"):
        self.recipient = recipient
        self.sender = sender
        self._messages: list[str] = []
        self._log: list[dict] = []

    def send(self, message: str) -> bool:
        if not isinstance(message, str):
            raise TypeError(f"message must be str, got {type(message).__name__}")
        if not self.recipient:
            return False  # «получатель не задан» — имитация ошибки отправки

        # Имитация SMTP-сеанса: фиксируем «письмо» в журнале и списке.
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "from": self.sender,
            "to": self.recipient,
            "subject": "Triangle result",
            "body": message,
        }
        self._log.append(entry)
        self._messages.append(message)
        return True

    def get_sent_messages(self) -> list[str]:
        return list(self._messages)

    def get_sent_log(self) -> list[dict]:
        """Полный журнал «отправленных писем» — для отладки и тестов."""
        return list(self._log)