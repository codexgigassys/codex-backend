import smtplib
from email.mime.text import MIMEText
from db_pool import *


def send_mail(toaddrs,subject,text):

    fromaddr = env.get('mailsender').get('fromaddr')

    msg = MIMEText(text)
    msg['Subject'] = subject
    msg['From'] = fromaddr
    msg['To'] = toaddrs

    # Credentials (if needed)
    username = env.get('mailsender').get('username')
    password = env.get('mailsender').get('password')

    # The actual mail send
    server = smtplib.SMTP_SSL(env.get('mailsender').get('smtp_host'),env.get('mailsender').get('smtp_ssl_port'))
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs,  msg.as_string())
    server.quit()
