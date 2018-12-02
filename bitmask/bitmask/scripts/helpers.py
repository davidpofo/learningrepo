# -*- coding: utf-8 -*-

from scripts import tabledef
from flask import session
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import bcrypt
import uuid
from pywallet import wallet

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    s = get_session()
    s.expire_on_commit = False
    try:
        yield s
        s.commit()
    except:
        s.rollback()
        raise
    finally:
        s.close()


def get_session():
    return sessionmaker(bind=tabledef.engine)()


def get_user():
    username = session['username']
    with session_scope() as s:
        user = s.query(tabledef.User).filter(tabledef.User.username.in_([username])).first()
        return user


def get_wallets():
    username = session['username']
    with session_scope() as s:
        wallets = s.query(tabledef.MPK).filter(tabledef.MPK.username.in_([username])).order_by("id desc").all()
        return wallets


def remove_wallet(id):
    username = session['username']
    with session_scope() as s:
        wallet = s.query(tabledef.MPK).filter(tabledef.MPK.id.in_([id]), tabledef.MPK.username.in_([username])).first()
        s.delete(wallet)


def get_wallet(url):
    with session_scope() as s:
        wallet = s.query(tabledef.MPK).filter(tabledef.MPK.url.in_([url])).first()
    return wallet


def get_address(donation):
    try:
        address = wallet.create_address(network="BTC", xpub=donation.mpk, child=donation.depth)
        return address["address"]
    except:
        return False


def add_user(username, password):
    with session_scope() as s:
        u = tabledef.User(username=username, password=password.decode('utf-8'))
        s.add(u)
        s.commit()


def change_user(**kwargs):
    username = session['username']
    with session_scope() as s:
        user = s.query(tabledef.User).filter(tabledef.User.username.in_([username])).first()
        for arg, val in kwargs.items():
            if val != "":
                setattr(user, arg, val)
        s.commit()


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())


def credentials_valid(username, password):
    with session_scope() as s:
        user = s.query(tabledef.User).filter(tabledef.User.username.in_([username])).first()
        if user:
            return bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))
        else:
            return False


def username_taken(username):
    with session_scope() as s:
        return s.query(tabledef.User).filter(tabledef.User.username.in_([username])).first()


def add_key(title, mpk):
    username = session['username']
    url = uuid.uuid4().hex.upper()[0:10].lower()
    try:
        wallet.create_address(network="BTC", xpub=mpk)
        with session_scope() as s:
            u = tabledef.MPK(username=username, mpk=mpk, title=title, url=url)
            s.add(u)
            s.commit()
        return True
    except:
        return False
