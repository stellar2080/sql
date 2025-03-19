import datetime
from sqlmodel import Field

import reflex as rx

class User(rx.Model, table=True):

    user_id: str = Field(primary_key=True)
    username: str
    password: str
    email: str

class Settings(rx.Model, table=True):

    user_id: str = Field(primary_key=True)
    accent_color: str
    gray_color: str
    radius: str
    scaling: str

class AIConfig(rx.Model, table=True):

    user_id: str = Field(primary_key=True)
    MAX_ITERATIONS: int
    DO_SAMPLE: bool
    TEMPERATURE: float
    TOP_K: int
    TOP_P: float
    MAX_TOKENS: int
    N_RESULTS: int
    E_HINT_THRESHOLD: float
    E_COL_THRESHOLD: float
    E_VAL_THRESHOLD: float
    E_COL_STRONG_THRESHOLD: float
    E_VAL_STRONG_THRESHOLD: float
    F_HINT_THRESHOLD: float
    F_LSH_THRESHOLD: float
    F_COL_THRESHOLD: float
    F_VAL_THRESHOLD: float
    F_COL_STRONG_THRESHOLD: float
    F_VAL_STRONG_THRESHOLD: float
    G_HINT_THRESHOLD: float
    LLM_HOST: str
    LLM_PORT: int