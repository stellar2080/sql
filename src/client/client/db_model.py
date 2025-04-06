from sqlmodel import Field, JSON, TEXT, DateTime
import reflex as rx
from datetime import datetime

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
    platform: str
    model: str
    api_key: str
    LLM_HOST: str
    LLM_PORT: int
    target_db_url: str
    MAX_ITERATIONS: int
    DO_SAMPLE: bool
    TEMPERATURE: float
    TOP_P: float
    MAX_TOKENS: int
    N_RESULTS: int
    E_HINT_THRESHOLD: float
    E_COL_THRESHOLD: float
    E_VAL_THRESHOLD: float
    E_COL_STRONG_THRESHOLD: float
    E_VAL_STRONG_THRESHOLD: float
    F_HINT_THRESHOLD: float
    F_COL_THRESHOLD: float
    F_LSH_THRESHOLD: float
    F_VAL_THRESHOLD: float
    F_COL_STRONG_THRESHOLD: float
    F_VAL_STRONG_THRESHOLD: float
    G_HINT_THRESHOLD: float

class ChatRecord(rx.Model, table=True):

    id: int | None = Field(default=None, primary_key=True)
    user_id: str
    question: str = Field(sa_type=TEXT)
    sql: str = Field(sa_type=TEXT)
    sql_result: dict = Field(sa_type=JSON)
    create_time: datetime = Field(sa_type=DateTime)