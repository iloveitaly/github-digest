#!/usr/bin/env -S ipython -i

import asyncio
from pathlib import Path

from decouple import config
from dinghy.digest import make_digests_from_config

from github_digest.email import send_email

ROOT_DIRECTORY = Path(__file__).parent.parent.resolve()
DIGEST_TARGET = ROOT_DIRECTORY / "data/digest.html"

asyncio.run(make_digests_from_config("digest.yaml"))


send_email(
    html_content=DIGEST_TARGET.read_text(),
    subject="Digest",
    email_to="iloveitaly@gmail.com",
    email_auth=config("EMAIL_AUTH", cast=str),
)

# DIGEST_TARGET.unlink()
