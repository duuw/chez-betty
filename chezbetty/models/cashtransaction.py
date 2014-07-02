from .model import *
from .transaction import Transaction

class CashAccount(Versioned, Base):
    __tablename__ = "cash_accounts"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False, unique=True)
    balance = Column(Numeric, nullable=False)

    def __init__(self, name):
        self.name = name
        self.balance = 0.0


def make_cash_account(name):
    t = DBSession.query(CashAccount).filter(CashAccount.name == name).first()
    if t:
        return t
    t = CashAccount(name)
    DBSession.add(t)
    DBSession.flush()
    return t


class CashTransaction(Base):
    __tablename__ = 'cash_transactions'

    id = Column(Integer, primary_key=True, nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True, unique=True)
    transaction = relationship(Transaction, backref=backref("cash_transaction", uselist=False), uselist=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    amount = Column(Numeric, nullable=False)

    to_account_id = Column(Integer, ForeignKey("cash_accounts.id"))
    from_account_id = Column(Integer, ForeignKey("cash_accounts.id"))

    to_account = relationship(CashAccount,
        foreign_keys=[to_account_id,],
        backref="transactions_to"
    )

    from_account = relationship(CashAccount,
        foreign_keys=[from_account_id,],
        backref="transactions_from"
    )

    def __init__(self, from_acct, to_acct, amount, transaction, user):
        self.from_account_id = from_acct.id if from_acct else None
        self.to_account_id = to_acct.id if to_acct else None
        self.amount = amount
        self.transaction_id = transaction.id if transaction else None
        self.user_id = user.id if user else None
        if to_acct:
            to_acct.balance += amount
        if from_acct:
            from_acct.balance -= amount

    def __str__(self):
        return "<CashTransaction (%i: %s -> %s: $%f)>" % (
                self.id,
                self.from_account_id.name,
                self.to_account.name,
                self.amount)


class CashDeposit(CashTransaction):
    def __init__(self, amount, transaction):
        c_cashbox = make_cash_account("cashbox")
        CashTransaction.__init__(self, None, c_cashbox, amount, transaction, None)


class CashSpend(CashTransaction):
    def __init__(self, amount, transaction, user=None):
        c_chezbetty = make_cash_account("chezbetty")
        c_store = make_cash_account("store")
        CashTransaction.__init__(self, c_chezbetty, c_store, amount, transaction, user)


class BTCCashDeposit(CashTransaction):
    def __init__(self, amount, transaction):
        c_chezbetty = make_cash_account("chezbetty")
        CashTransaction.__init__(self, None, c_chezbetty, amount, transaction, None)

