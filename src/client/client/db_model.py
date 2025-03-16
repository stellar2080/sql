import datetime
from sqlmodel import Field

import reflex as rx

class User(rx.Model, table=True):

    user_id: str = Field(primary_key=True)
    username: str
    password: str
    email: str