from flask import session, Flask
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class EmailUtils:
    def __init__(self):
        self.app=Flask(__name__)
        self.mail=Mail(self.app)
        self.app.config["MAIL_SERVER"]=os.getenv('MAIL_SERVER')
        self.app.config["MAIL_PORT"]=int(os.getenv('MAIL_PORT'))
        self.app.config["MAIL_USERNAME"]=os.getenv('MAIL_USERNAME')
        self.app.config['MAIL_PASSWORD']=os.getenv('MAIL_PASSWORD')
        self.app.config['MAIL_USE_TLS']=False
        self.app.config['MAIL_USE_SSL']=True
        self.mail=Mail(self.app)

    def send_email(self,recipient_email,content):
        subject = content.get("subject","Notification")
        email_body = content.get("body")
        msg = Message(subject=subject, sender='ping2sarthak@gmail.com', recipients=[recipient_email])
        msg.body = email_body
        self.mail.send(msg)
