"""Unit tests module."""
import pytest
from app import BankAccount, InsufficientFunds


class TestBankAccount:
    """Unit tests for bank account app."""

    def test_deposit_positive(self):
        """Deposit positive scenario."""
        b_acc = BankAccount(initial_balance=100)
        b_acc.deposit(amount=50)
        assert b_acc.balance == 150, 'Incorrect balance calculations'

    def test_deposit_zero(self):
        """Zero Deposit check."""
        b_acc = BankAccount(initial_balance=100)
        with pytest.raises(ValueError) as v_err:
            b_acc.deposit(amount=0)
        assert 'Deposit amount must be positive' in str(v_err)

    def test_deposit_negative(self):
        """Negative Deposit check."""
        b_acc = BankAccount(initial_balance=50)
        with pytest.raises(ValueError) as v_err:
            b_acc.deposit(amount=-10)
        assert 'Deposit amount must be positive' in str(v_err), 'Wrong value error message'

    def test_withdraw_positive(self):
        """Withdraw positive scenario."""
        b_acc = BankAccount(initial_balance=50)
        b_acc.withdraw(amount=40)
        assert b_acc.balance == 10, 'Incorrect balance calculations'

    def test_withdraw_more_than_balance(self):
        """Not sufficient funds scenario."""
        b_acc = BankAccount(initial_balance=250)
        with pytest.raises(InsufficientFunds) as if_err:
            b_acc.withdraw(amount=300)
        assert 'Insufficient funds' in str(if_err), 'Wrong insufficient funds message'

    def test_withdraw_zero(self):
        """Zero Withdraw check."""
        b_acc = BankAccount(initial_balance=250)
        with pytest.raises(ValueError) as v_err:
            b_acc.withdraw(amount=0)
        assert 'Withdrawal amount must be positive' in str(v_err), 'Wrong value error message'

    def test_transfer_positive(self):
        """Transfer positive scenario."""
        b_acc1 = BankAccount(initial_balance=1000)
        b_acc2 = BankAccount(initial_balance=100)
        b_acc1.transfer(other_account=b_acc2, amount=400)
        assert b_acc1.balance == 600, 'Incorrect withdraw calculations for first bank account'
        assert b_acc2.balance == 500, 'Incorrect deposit calculations for second bank account'

    def test_transfer_incorrect_account_object(self):
        """Transfer to incorrect account."""
        b_acc1 = BankAccount(initial_balance=1000)
        b_acc2 = type('SomeFakeBankAccount', (), {'get_balance': lambda: 100})
        with pytest.raises(TypeError) as t_err:
            b_acc1.transfer(other_account=b_acc2, amount=400)
        assert 'Other account must be a BankAccount instance' in str(t_err), 'Wrong TypeError message'

    def test_balance_positive(self):
        """Get balance positive scenario."""
        test_balance = 728.26
        b_acc = BankAccount(initial_balance=test_balance)
        assert b_acc.get_balance() == test_balance, 'Incorrect balance calculations'

    def test_balance_default(self):
        """Get balance with default value scenario."""
        b_acc = BankAccount()
        assert b_acc.get_balance() == 0, 'Incorrect default balance'
