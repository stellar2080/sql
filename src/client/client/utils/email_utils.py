import re
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import random

def send_email(msg_to):
    msg_from = 'stellar2080@163.com' 
    passwd = 'WKeWFnRRC6v2mEkt' 
    subject = "Text2SQL系统注册验证码" 
 
    captcha = random.randint(100000, 999999)
    captcha_str = str(captcha)
    send_info = f'您的注册验证码为：{captcha_str}，5分钟内有效，请勿转发给他人！'
    msg = MIMEText(send_info, 'plain', 'utf-8')
 
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = msg_from
    msg['To'] = msg_to
 
    s = smtplib.SMTP_SSL("smtp.163.com", 465)
    s.login(msg_from, passwd)
    s.sendmail(msg_from, msg_to, msg.as_string())
    return captcha_str

def validate_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@(163|qq)\.com$'
    if re.match(pattern, email):
        return True
    else:
        return False