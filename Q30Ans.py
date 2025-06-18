from __future__ import annotations
from datetime import datetime
from threading import Lock
from typing import List

input("Виконав Іванченко Даніїл, КІб-1-23-4.0д")

class _SingletonMeta(type):
    """
    Клас-метаклас робить усіх своїх нащадків singleton-ами.
    Потікобезпечне ліниве створення об’єкта.
    """
    _instances: dict[type, object] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:                      # double-checked locking
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Logger(metaclass=_SingletonMeta):
    """Патерн Singleton: завжди повертає один і той самий об’єкт."""
    
    def __init__(self) -> None:
        self._log: List[str] = []

    def write(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self._log.append(entry)
        print(entry)                # одночасно пишемо на консоль

    def history(self) -> List[str]:
        """Повертає копію журналу (read-only)."""
        return list(self._log)

class InsufficientFundsError(Exception):
    """Кидається, коли на рахунку бракує грошей для операції."""
    pass

class BankAccount:
    def __init__(self, account_number: str, initial_balance: float = 0.0) -> None:
        if initial_balance < 0:
            raise ValueError("Початковий баланс не може бути від’ємним")

        self.account_number = account_number
        self.balance = initial_balance
        self._logger = Logger()
        self._logger.write(f"Account {self.account_number} opened with balance {self.balance:.2f}₴")

    def deposit(self, amount: float) -> None:
        self._validate_amount(amount)
        self.balance += amount
        self._logger.write(f"Account {self.account_number}: +{amount:.2f}₴ → new balance {self.balance:.2f}₴")

    def withdraw(self, amount: float) -> None:
        self._validate_amount(amount)
        if amount > self.balance:
            self._logger.write(
                f"Account {self.account_number}: FAILED withdrawal {amount:.2f}₴ (balance {self.balance:.2f}₴)"
            )
            raise InsufficientFundsError(
                f"На рахунку {self.balance:.2f}₴; неможливо зняти {amount:.2f}₴"
            )
        self.balance -= amount
        self._logger.write(f"Account {self.account_number}: -{amount:.2f}₴ → new balance {self.balance:.2f}₴")

    @staticmethod
    def _validate_amount(amount: float) -> None:
        if amount <= 0:
            raise ValueError("Сума має бути додатною")

if __name__ == "__main__":
    acc = BankAccount("UA123456789", 1000)
    acc.deposit(250)
    try:
        acc.withdraw(1500)          # навмисно перевищуємо баланс
    except InsufficientFundsError as ex:
        print("⚠️", ex)

    acc.withdraw(200)

    # увесь журнал
    print("\n─── ІСТОРІЯ ───")
    for line in Logger().history():
        print(line)
