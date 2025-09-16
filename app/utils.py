# from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
# from pydantic import EmailStr
# import os

# conf = ConnectionConfig(
#     MAIL_USERNAME = os.getenv("MAIL_USERNAME", "your_email@example.com"),
#     MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "yourpassword"),
#     MAIL_FROM = os.getenv("MAIL_FROM", "your_email@example.com"),
#     MAIL_PORT = 587,
#     MAIL_SERVER = "smtp.gmail.com",
#     MAIL_TLS = True,
#     MAIL_SSL = False,
#     USE_CREDENTIALS = True,
#     VALIDATE_CERTS = True
# )

# def send_email(to: str, subject: str, body: str):
#     message = MessageSchema(
#         subject=subject,
#         recipients=[to],
#         body=body,
#         subtype="plain"
#     )
#     fm = FastMail(conf)
#     import asyncio
#     asyncio.run(fm.send_message(message))
