# bank_account.py

class InsufficientFunds(Exception):
    pass


class BankAccount:
    def __init__(self, initial_balance=0):
        self.balance = initial_balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise InsufficientFunds("Insufficient funds")
        self.balance -= amount

    def transfer(self, other_account, amount):
        if not isinstance(other_account, BankAccount):
            raise TypeError("Other account must be a BankAccount instance")
        self.withdraw(amount)
        other_account.deposit(amount)

    def get_balance(self):
        return self.balance
