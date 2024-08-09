import asyncio
from pathlib import Path

from bs4 import BeautifulSoup
from decouple import config
from dinghy.digest import make_digests_from_config

# IMPORTANT!
import github_digest.patch
from github_digest.email import send_email

ROOT_DIRECTORY = Path(__file__).parent.parent.resolve()
DIGEST_TARGET = ROOT_DIRECTORY / "data/digest.html"
DIGEST_YAML = ROOT_DIRECTORY / "data/digest.yaml"


def extract_title(html_file_path):
    html_content = html_file_path.read_text()
    soup = BeautifulSoup(html_content, features="html.parser")
    title_tag = soup.title
    return title_tag.string.strip() if title_tag else None


def main(since):
    asyncio.run(make_digests_from_config(str(DIGEST_YAML)))

    title = extract_title(DIGEST_TARGET)

    send_email(
        html_content=DIGEST_TARGET.read_text(),
        subject=title,
        email_to="iloveitaly@gmail.com",
        email_auth=config("EMAIL_AUTH", cast=str),
    )

    # DIGEST_TARGET.unlink()

    print("digest creation complete")
