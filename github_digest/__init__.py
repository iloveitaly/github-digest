import asyncio
import datetime
import logging
import os
import tempfile
from pathlib import Path

import click
from bs4 import BeautifulSoup
from dinghy.digest import make_digests_from_config

# IMPORTANT! Do not remove and must be run first.
import github_digest.patch as _
from github_digest.email import send_email

ROOT_DIRECTORY = Path(__file__).parent.parent.resolve()
DIGEST_TARGET = ROOT_DIRECTORY / "data/digest.html"
DIGEST_YAML = ROOT_DIRECTORY / "data/digest.yaml"
DEFAULT_GITHUB_USER = "iloveitaly"

logger = logging.getLogger(__name__)

# set level based on LOG_LEVEL env var
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=log_level)


def extract_title(html_file_path) -> str | None:
    "grab the title from the generated dingy HTML"
    html_content = html_file_path.read_text()
    soup = BeautifulSoup(html_content, features="html.parser")
    title_tag = soup.title
    return title_tag.string.strip() if title_tag else None


def main(since: datetime.datetime, github_user: str, email_to: str, email_from: str, email_auth: str, dry_run: bool):
    # the underlying digest library expects a relative date string
    # this is parsed using a custom regex in the library
    relative_minutes = int((datetime.datetime.now() - since).total_seconds() / 60)
    relative_minutes_formatted = f"{relative_minutes}m"

    logger.info(f"creating digest since {relative_minutes_formatted}")

    # create a tmp file copied from DIGEST_TARGET and find/replace DEFAULT_GITHUB_USER with github_user
    digest_content = DIGEST_YAML.read_text()
    digest_content = digest_content.replace(DEFAULT_GITHUB_USER, github_user)    

    # Create temp file with replaced content
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as tmp_file:
        digest_content = DIGEST_YAML.read_text()
        digest_content = digest_content.replace(DEFAULT_GITHUB_USER, github_user)
        Path(tmp_file.name).write_text(digest_content)
        tmp_yaml_path = tmp_file.name

        asyncio.run(
            make_digests_from_config(str(tmp_yaml_path), since=relative_minutes_formatted)
        )


    title = extract_title(DIGEST_TARGET)
    title = f"GitHub {title}"

    if dry_run:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp_file:
            tmp_file.write(DIGEST_TARGET.read_text())
            logger.info(f"HTML output: {tmp_file.name}")
    else:
        send_email(
            html_content=DIGEST_TARGET.read_text(),
            subject=title,
            email_to=email_to,
            email_from=email_from,
            email_auth=email_auth,
        )

    # TODO can't hurt to leave the file around, right?
    # DIGEST_TARGET.unlink()

    logger.info("digest creation complete")


# adds GITHUB_DIGEST_ as a prefix to all ENV variables
@click.command(context_settings={"auto_envvar_prefix": "GITHUB_DIGEST"})
@click.option(
    "--since",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Date to pull notifications since in YYYY-MM-DD format",
    required=True,
)
@click.option("--github-username", help="Who is the target GitHub user for this digest", required=True)
@click.option("--email-to", help="Who to send the digest to", required=True)
@click.option("--email-from", help="Who to send the digest from")
@click.option("--email-auth", help="Email authentication string", required=True)
@click.option("--dry-run", help="Output HTML instead of sending an email", is_flag=True)
def cli(since, github_username, email_to, email_from, email_auth, dry_run):
    main(since, github_username, email_to, email_from, email_auth, dry_run)
