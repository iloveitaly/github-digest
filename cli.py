import os
from datetime import datetime, timedelta, timezone

import click

from digest import main


def default_since():
    since = "1w"
    since_date = datetime.now(timezone.utc) - timedelta(
        weeks=1 if since == "1w" else int(since[:-1])
    )
    return since_date.strftime("%m/%d/%Y")


def parse_date(ctx, param, value):
    try:
        return datetime.strptime(value, "%m/%d/%Y")
    except ValueError:
        raise click.BadParameter("Date must be in MM/DD/YYYY format")


@click.command()
@click.option(
    "--since",
    default=default_since,
    callback=parse_date,
    help="Date to pull notifications since in MM/DD/YYYY format",
)
@click.option("--github-token", default=os.getenv("GITHUB_TOKEN"), help="GitHub token")
@click.option(
    "--target-project-ids",
    default=os.getenv("TARGET_PROJECT_IDS"),
    help="Target project IDs",
)
@click.option(
    "--email-auth",
    default=os.getenv("EMAIL_AUTH"),
    help="Email authentication string",
)
@click.option(
    "--email-to",
    default=os.getenv("EMAIL_TO"),
    help="Email recipient(s)",
)
def cli(since, github_token, target_project_ids, email_auth, email_to):
    main(since, github_token, target_project_ids, email_auth, email_to)


if __name__ == "__main__":
    cli()
