import os
import sys
import reflex as rx

CLIENT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CLIENT_PATH)

config = rx.Config(
    app_name="client",
    db_url="mysql+pymysql://stellar:123456@127.0.0.1/reflex",
    redis_url='redis://default:123456@127.0.0.1:6379/0',
    redis_lock_expiration=100000,  # Redis锁的最大过期时间(毫秒)
    redis_lock_warning_threshold=1000,  # Redis锁的警告阈值(毫秒) 
    redis_token_expiration=3600, # Redis令牌的过期时间(秒)
    frontend_port=3000,
    backend_port=8001,
    loglevel='info'
)