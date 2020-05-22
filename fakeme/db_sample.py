from datetime import datetime
from random import getrandbits
from typing import Dict, Text

from gino.crud import _Create
from gino.ext.sanic import Gino
from sqlalchemy import and_

db = Gino()


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.String(24), unique=True, primary_key=True)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(24))
    name = db.Column(db.String())
    family_name = db.Column(db.String())
    phone = db.Column(db.String())
    address = db.Column(db.String())
    registered_at = db.Column(db.DateTime(), default=lambda: datetime.now().isoformat())

    def to_dict(self):
        user_dict = super().to_dict()
        del user_dict["password_hash"]
        return user_dict

    async def get_user_all_products(self, active: bool = True) -> Dict:
        """ get all accounts and cards (ids) for user, set `activate=False` to get deactivated accounts """
        products = {}
        products_models = Product.__subclasses__()
        for product_model in products_models:
            accounts = await product_model.query.where(
                and_(User.id == self.id, product_model.active == active)
            ).gino.all()
            products[product_model.__tablename__] = [
                {product.name if product.name else product.id: product.id}
                for product in accounts
            ]
        return products

    async def get_user_products_by_type(
        self, product_type: Text, active: bool = True
    ) -> Dict:
        """ get all account_ids of `product_type` for user, set `activate=False` to get deactivated accounts """
        products = {}
        product_model = [
            x for x in Product.__subclasses__() if x.__tablename__ == product_type
        ][0]
        accounts = await product_model.query.where(
            and_(product_model.user_id == self.id, product_model.active == active)
        ).gino.all()
        products[product_model.__tablename__] = [
            {product.name if product.name else product.id: product.id}
            for product in accounts
        ]
        return products

    @staticmethod
    async def create(*args, **kwargs):
        if "registered_at" not in kwargs:
            kwargs["registered_at"] = datetime.now()
        return await _Create().__get__(None, owner=User)(*args, **kwargs)


class Product:
    """ common columns for Products (accounts, cards) """

    id = db.Column(db.String(), unique=True, primary_key=True, autoincrement=False)
    user_id = db.Column(db.String(), db.ForeignKey("users.id"))
    name = db.Column(db.String())
    creation_datetime = db.Column(db.DateTime())
    balance = db.Column(db.Integer(), default=0)
    active = db.Column(db.Boolean(), default=True)

    @staticmethod
    async def create_product(model):

        # TODO: this is temporary solution, Sequences from PostgreSQL does not work correct with Gino
        _id = getrandbits(42)

        async def create(*args, **kwargs):
            if not kwargs.get("creation_datetime"):
                kwargs["creation_datetime"] = datetime.now()
            if not kwargs.get("id"):
                kwargs["id"] = str(_id)
            return await _Create().__get__(None, owner=model)(*args, **kwargs)

        return create


class SavingAccount(db.Model, Product):

    __tablename__ = "saving_accounts"

    interest_rate = db.Column(db.Numeric())

    @staticmethod
    async def create(*args, **kwargs):
        return await (await Product.create_product(SavingAccount))(*args, **kwargs)


class CheckingAccount(db.Model, Product):

    __tablename__ = "checking_accounts"

    interest_rate = db.Column(db.Numeric())

    @staticmethod
    async def create(*args, **kwargs):
        return await (await Product.create_product(CheckingAccount))(*args, **kwargs)


class CreditCard(db.Model, Product):

    __tablename__ = "credit_cards"

    @staticmethod
    async def create(*args, **kwargs):
        return await (await Product.create_product(CreditCard))(*args, **kwargs)


class UserToken(db.Model):

    __tablename__ = "users_tokens"

    token = db.Column(db.String(), unique=True, primary_key=True, autoincrement=False)
    user_id = db.Column(db.String(), db.ForeignKey("users.id"))
    user_agent = db.Column(db.String())


class AccountAction:
    """ common columns for Account Actions (accounts, cards) """

    id = db.Column(db.BigInteger(), unique=True, primary_key=True)
    title = db.Column(db.String())
    event_time = db.Column(db.DateTime())
    amount = db.Column(db.Integer())
    account_balance = db.Column(db.String())

    @staticmethod
    async def create_action(model):

        _id = getrandbits(42)

        async def create(*args, **kwargs):
            if not kwargs.get("event_time"):
                kwargs["event_time"] = datetime.now()
            if not kwargs.get("id"):
                kwargs["id"] = str(_id)
            return await _Create().__get__(None, owner=model)(*args, **kwargs)

        return create

    @classmethod
    async def get_all_actions(cls, account_id):
        """ return full actions list for account id """
        actions_list = await cls.query.where(cls.account_id == account_id).gino.all()
        return actions_list


class SavingAccountAction(db.Model, AccountAction):

    __tablename__ = "saving_accounts_actions"

    account_id = db.Column(db.String(), db.ForeignKey("saving_accounts.id"))

    @staticmethod
    async def create(*args, **kwargs):
        return await (await AccountAction.create_action(SavingAccountAction))(
            *args, **kwargs
        )


class CheckingAccountAction(db.Model, AccountAction):

    __tablename__ = "checking_accounts_actions"

    account_id = db.Column(db.String(), db.ForeignKey("checking_accounts.id"))

    @staticmethod
    async def create(*args, **kwargs):
        return await (await AccountAction.create_action(CheckingAccountAction))(
            *args, **kwargs
        )


class CreditCardAction(db.Model, AccountAction):

    __tablename__ = "credit_cards_actions"

    account_id = db.Column(db.String(), db.ForeignKey("credit_cards.id"))

    @staticmethod
    async def create(*args, **kwargs):
        return await (await AccountAction.create_action(CreditCardAction))(
            *args, **kwargs
        )
