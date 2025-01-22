import datetime
import os

from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from github_digest import cli
from github_digest.internet import wait_for_internet_connection

last_synced: datetime.datetime | None = None


def get_initial_start_date():
    return datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=3)


def handle_click_exit(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except SystemExit as e:
            if e.code != 0:
                raise

    return wrapper


def job():
    global last_synced

    print(f"Running job with last_synced: {last_synced}")

    # set through env so we can use the same CLI interface
    os.environ["GITHUB_DIGEST_SINCE"] = last_synced.strftime("%Y-%m-%d")

    wait_for_internet_connection()

    handle_click_exit(cli)()

    last_synced = datetime.datetime.now()


def cron():
    global last_synced

    if datetime.datetime.now().astimezone().tzinfo.utcoffset(None) != datetime.timedelta(0):
        print("WARNING: System timezone is not UTC. This may cause unexpected behavior since GitHub GraphQL assumes UTC.")

    last_synced = get_initial_start_date()

    # run at midnight by default, since 
    schedule = os.environ.get("SCHEDULE", "0 6 * * *")

    print(f"Running on schedule: {schedule}")

    scheduler = BlockingScheduler()
    scheduler.add_job(job, CronTrigger.from_crontab(schedule))
    scheduler.start()

if __name__ == "__main__":
    cron()
