# GitHub Email Digest

Why? Because GitHub's notification system is a complete mess and unusable.

This generates a nice email digest of all activity on your GitHub and sends it over email.

There's a nice docker image for deployment.

## How it works

There's a [poorly-named-but-great tool named dinghy which summarizes github activity.](https://github.com/nedbat/dinghy)

This project builds upon this library:

1. Runs it on a cron
2. Bundles a default config file
3. Converts HTML into a email-safe format
4. Sends an email

## Usage

```shell
❯ github-digest --help
Usage: github-digest [OPTIONS]

Options:
  --since [%Y-%m-%d]      Date to pull notifications since in YYYY-MM-DD
                          format  [required]
  --github-username TEXT  Who is the target GitHub user for this digest
                          [required]
  --email-to TEXT         Who to send the digest to  [required]
  --email-from TEXT       Who to send the digest from
  --email-auth TEXT       Email authentication string  [required]
  --dry-run               Output HTML instead of sending an email
  --help                  Show this message and exit.
```

### Docker

You can use the [docker image](./docker-compose.yml) to run the digest as well. I've really [liked resend](https://resend.com/emails) for SMTP.

## Development

Simulating a cron run:

```python
from datetime import datetime
import os
from github_digest import cli

last_synced_raw = '2025-01-01 01:12:13.232395+00:00'
last_synced = datetime.fromisoformat(last_synced_raw)

os.environ["GITHUB_DIGEST_GITHUB_USERNAME"] = "iloveitaly"
os.environ["GITHUB_DIGEST_SINCE"] = last_synced.strftime("%Y-%m-%d")

cli()
```

You can do this within a container as well:

```bash
pip install ipython
ipython
```

## Deployment

I had some trouble building the container with nixpacks (my favorite build tool) because of required libraries. Here's a
command I used to help replicate the prod environment locally

```bash
nixpacks build . --name github-digest-local --libs=cairo # you can play around with various config settings

docker run --env GITHUB_TOKEN --env GITHUB_DIGEST_EMAIL_AUTH --env GITHUB_DIGEST_EMAIL_TO --env GITHUB_DIGEST_EMAIL_FROM -it github-digest-local:latest bash -l
```

