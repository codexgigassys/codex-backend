import smtplib
from email.mime.text import MIMEText
from db_pool import *


def send_mail(toaddrs,subject,text):
    if toaddrs is None or len(toaddrs)==0:
        return
    fromaddr = envget('mailsender.fromaddr')

    msg = MIMEText(text)
    msg['Subject'] = subject
    msg['From'] = fromaddr
    msg['To'] = toaddrs

    # Credentials (if needed)
    username = envget('mailsender.username')
    password = envget('mailsender.password')

    # The actual mail send
    server = smtplib.SMTP_SSL(envget('mailsender.smtp_host'),envget('mailsender.smtp_ssl_port'))
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs,  msg.as_string())
    server.quit()
