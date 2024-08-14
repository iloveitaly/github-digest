import os
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from github_digest import cli

last_synced = None


def get_initial_start_date():
    return datetime.utcnow() - timedelta(days=3)


def job():
    global last_synced

    print(f"Running job with last_synced: {last_synced}")

    os.environ["GITHUB_DIGEST_SINCE"] = last_synced.strftime("%Y-%m-%d")

    cli()

    last_synced = datetime.utcnow()


def cron():
    global last_synced

    last_synced = get_initial_start_date()

    schedule = os.environ.get("SCHEDULE", "0 6 * * *")

    print(f"Running on schedule: {schedule}")

    scheduler = BlockingScheduler()
    scheduler.add_job(job, CronTrigger.from_crontab(schedule))
    scheduler.start()


if __name__ == "__main__":
    cron()
