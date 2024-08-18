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


@click.command(context_settings={"auto_envvar_prefix": "GITHUB_DIGEST"})
@click.option(
    "--since",
    default=default_since,
    callback=parse_date,
    help="Date to pull notifications since in MM/DD/YYYY format",
)
@click.option("--email-to", help="Email recipient(s)", required=True)
@click.option(
    "--email-from",
    help="Email recipient(s)",
)
@click.option("--email-auth", help="Email authentication string", required=True)
def cli(since, email_to, email_from, email_auth):
    main(since, email_to, email_from, email_auth)


if __name__ == "__main__":
    cli()
