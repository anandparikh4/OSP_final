from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from decouple import config

def send_email(subject,text,receive_address):
    try:
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
        sender_mail = config('MAIL')
        sender_password = config('PASSWORD')
        smtp.login(sender_mail, sender_password)
        message = MIMEMultipart()
        message['Subject'] = subject
        message.attach(MIMEText(text))
        smtp.sendmail(from_addr=config('MAIL'),to_addrs=receive_address, msg=message.as_string())
        smtp.quit()
        return True,"Mail sent successfully"
    except:
        raise

def manager_sign_up(**kwargs):
    from backend.classes.user import Manager
    try:
        new_manager = Manager.create_manager(**kwargs)
        return True,new_manager
    except Exception as ex:
        return False, str(ex)

def seller_sign_up(**kwargs):
    from backend.classes.user import Seller
    try:
        new_seller = Seller.create_seller(**kwargs)
        return True,new_seller
    except Exception as ex:
        return False, str(ex)

def buyer_sign_up(**kwargs):
    from backend.classes.user import Buyer
    try:
        new_buyer = Buyer.create_buyer(**kwargs)
        return True,new_buyer
    except Exception as ex:
        return False, str(ex)
