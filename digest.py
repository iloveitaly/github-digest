import logging
from collections import defaultdict
from datetime import datetime

from github import Github
from github.GithubException import GithubException

from github_digest.email import send_email_markdown

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_github_notifications(since_date: datetime, token: str, repo_ids=None):
    g = Github(token)
    notifications = []
    for notification in g.get_user().get_notifications(since=since_date):
        if not repo_ids or notification.repository.id in repo_ids:
            notifications.append(notification)
    return notifications


def enhance_pr(notification, token):
    g = Github(token)
    pr = g.get_repo(notification.repository.full_name).get_pull(notification.subject.id)
    return pr


def group_notifications_by_repo(notifications, author, token):
    grouped = {
        "issues": defaultdict(list),
        "prs": defaultdict(list),
    }

    for notification in notifications:
        repo_name = notification.repository.full_name
        if notification.subject.type == "Issue":
            grouped["issues"][repo_name].append(notification)
        elif notification.subject.type == "PullRequest":
            pr = enhance_pr(notification, token)
            if pr.user.login == author:
                grouped["prs"][repo_name].append(pr.raw_data)
            else:
                grouped["issues"][repo_name].append(notification.raw_data)

    return grouped


def format_notifications(grouped_notifications):
    markdown_text = ""
    for repo, notifications in grouped_notifications.items():
        if notifications:
            repo_url = notifications[0].get("repository", {}).get("html_url", "#")
            markdown_text += f"## [{repo}]({repo_url})\n\n"
            for notification in notifications:
                notification_title = notification.get("subject", {}).get(
                    "title", "No title available"
                )
                notification_url = notification.get("subject", {}).get("url", "#")
                markdown_text += f"- [{notification_title}]({notification_url})\n"
            markdown_text += "\n"
    return markdown_text


def get_github_user(token: str):
    g = Github(token)
    return g.get_user().login


def main(
    since_date: datetime, github_token: str, target_project_ids, email_auth, email_to
):
    if target_project_ids:
        target_project_ids = [int(id) for id in target_project_ids.split(",")]

    notifications = get_github_notifications(
        since_date, github_token, repo_ids=target_project_ids
    )
    author = get_github_user(github_token)
    grouped_notifications = group_notifications_by_repo(
        notifications, author, github_token
    )
    formatted_text = format_notifications(grouped_notifications)

    print(formatted_text)

    # Uncomment and use the below code to send an email, if needed.
    # if email_auth:
    #     subject_formatted = f"GitHub Digest {since_date.strftime('%m/%d/%Y')}-{datetime.now().strftime('%m/%d/%Y')}"
    #     send_email_markdown(
    #         markdown_content=formatted_text,
    #         subject=subject_formatted,
    #         email_auth=email_auth,
    #         email_to=email_to,
    #     )
