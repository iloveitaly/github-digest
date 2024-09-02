# GitHub Email Digest

Why? Because GitHub's notification system is a complete mess and unusable.

This generates a nice email digest of all activity on your GitHub and sends it over email.

There's a nice docker image for deployment.

## Usage

Simulating a cron run:

```python
from datetime import datetime
import os
from github_digest import cli

last_synced_raw = '2024-08-24 01:12:13.232395+00:00'
last_synced = datetime.fromisoformat(last_synced_raw)

os.environ["GITHUB_DIGEST_SINCE"] = last_synced.strftime("%Y-%m-%d")

cli()
```