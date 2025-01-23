import logging
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urlparse

import backoff
import css_inline

logger = logging.getLogger(__name__)


@backoff.on_exception(backoff.expo, ssl.SSLEOFError, max_tries=5)
def send_email(*, html_content, subject, email_to, email_from, email_auth):
    parsed_url = urlparse(email_auth)

    msg = MIMEMultipart()
    msg["From"] = email_from or parsed_url.username
    msg["To"] = email_to
    msg["Subject"] = subject

    logger.info(
        "creating email for %s, from %s",
        email_to,
        parsed_url.username,
    )

    inliner = css_inline.CSSInliner(keep_style_tags=True)
    inlined_content = inliner.inline(html_content)

    # (ROOT_DIRECTORY / "data/digest_inlined.html").write_text(inlined_content)

    msg.attach(MIMEText(inlined_content, "html"))

    with smtplib.SMTP_SSL(parsed_url.hostname, parsed_url.port) as server:
        logger.info("Sending email to %s", email_to)

        login_result = server.login(parsed_url.username, parsed_url.password)
        logger.info("Login result: %s", login_result)
        result = server.send_message(msg)
        logger.info("Send result: %s", result)
        server.quit()
