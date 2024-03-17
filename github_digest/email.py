import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urlparse

import markdown2

logger = logging.getLogger(__name__)


def send_email_markdown(*, markdown_content, subject, email_to, email_auth):
    parsed_url = urlparse(email_auth)
    html_content = markdown2.markdown(markdown_content)
    breakpoint()

    msg = MIMEMultipart()
    msg["From"] = os.environ.get("EMAIL_FROM", parsed_url.username)
    msg["To"] = email_to
    msg["Subject"] = subject

    logger.info(
        "creating email for %s, from %s, content length %i",
        email_to,
        parsed_url.username,
        len(markdown_content),
    )

    # TODO any sane HTML styling we can setup?
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL(parsed_url.hostname, parsed_url.port) as server:
        logger.info("Sending email to %s", email_to)

        login_result = server.login(parsed_url.username, parsed_url.password)
        logger.info("Login result: %s", login_result)
        result = server.send_message(msg)
        logger.info("Send result: %s", result)
        server.quit()
