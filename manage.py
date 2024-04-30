import json
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread

import pika


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voting_system.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


def addEmailToQueue(receiverEmail, jsonData):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='email_queue')
    message = json.dumps({'receiverEmail': receiverEmail, 'jsonData': jsonData})
    channel.basic_publish(exchange='', routing_key='email_queue', body=message)
    connection.close()


def sendEmail(receiverEmail, jsonData):
    sender = "markhallak@outlook.com"
    message = MIMEMultipart("alternative")
    message['From'] = sender
    message['To'] = receiverEmail
    message['Subject'] = "Flight Deleted"

    html = f"""
            <html>
            <body>
            Dear User,
            <br><br>
            Unfortunately, your flight <strong>#{jsonData['flight_number']}</strong> is not <strong>available</strong> anymore.
            <br><br>
            Best Regards,
            <br>
            Your Team
            </body>
            </html>
    """
    part = MIMEText(html, "html")
    message.attach(part)

    with smtplib.SMTP('smtp.outlook.com', 587) as server:
        server.starttls()
        server.login('your_account@outlook.com', 'your_password')
        server.sendmail(sender, receiverEmail, message.as_string())


def parse_email_info(body):
    return json.loads(body.decode('utf-8'))


def start_pika_consumer():
    def callback(ch, method, properties, body):
        email_info = parse_email_info(body)
        sendEmail(email_info['receiverEmail'], email_info['jsonData'])

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='email_queue')
    channel.basic_consume(queue='email_queue', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


if __name__ == '__main__':
    tp = Thread(target=start_pika_consumer)
    tp.start()
    main()
    tp.join()