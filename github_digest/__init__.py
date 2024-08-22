import asyncio
import datetime
from pathlib import Path

import click
from bs4 import BeautifulSoup
from decouple import config
from dinghy.digest import make_digests_from_config

# IMPORTANT!
import github_digest.patch as _
from github_digest.email import send_email

ROOT_DIRECTORY = Path(__file__).parent.parent.resolve()
DIGEST_TARGET = ROOT_DIRECTORY / "data/digest.html"
DIGEST_YAML = ROOT_DIRECTORY / "data/digest.yaml"


def extract_title(html_file_path) -> str | None:
    html_content = html_file_path.read_text()
    soup = BeautifulSoup(html_content, features="html.parser")
    title_tag = soup.title
    return title_tag.string.strip() if title_tag else None


def main(since: datetime.datetime, email_to, email_from, email_auth):
    # the underlying digest library expects a relative date string
    # this is parsed using a custom regex
    relative_minutes = int((datetime.datetime.now() - since).total_seconds() / 60)
    relative_minutes_formatted = f"{relative_minutes}m"

    print(f"creating digest since {relative_minutes_formatted}")

    asyncio.run(
        make_digests_from_config(str(DIGEST_YAML), since=relative_minutes_formatted)
    )

    title = extract_title(DIGEST_TARGET)
    title = f"GitHub {title}"

    send_email(
        html_content=DIGEST_TARGET.read_text(),
        subject=title,
        email_to=email_to,
        email_from=email_from,
        email_auth=email_auth,
    )

    # TODO can't hurt to leave the file around, right?
    # DIGEST_TARGET.unlink()

    print("digest creation complete")


@click.command(context_settings={"auto_envvar_prefix": "GITHUB_DIGEST"})
@click.option(
    "--since",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Date to pull notifications since in YYYY-MM-DD format",
    required=True,
)
@click.option("--email-to", help="Who to send the digest to", required=True)
@click.option("--email-from", help="Who to send the digest from")
@click.option("--email-auth", help="Email authentication string", required=True)
def cli(since, email_to, email_from, email_auth):
    main(since, email_to, email_from, email_auth)
