import logging
from collections import defaultdict
from datetime import datetime, timedelta

import requests

from github_digest.email import send_email_markdown

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def get_github_notifications(since_date: datetime, token: str, repo_ids=None):
    url = f"https://api.github.com/notifications?since={since_date.isoformat()}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    notifications = response.json()
    if repo_ids:
        notifications = [n for n in notifications if n["repository"]["id"] in repo_ids]
    return notifications


def group_notifications_by_repo(notifications):
    grouped = defaultdict(list)
    for notification in notifications:
        repo_name = notification["repository"]["full_name"]
        grouped[repo_name].append(notification)
    return dict(grouped)


def format_notifications(grouped_notifications):
    markdown_text = ""
    for repo, notifications in grouped_notifications.items():
        repo_url = notifications[0]["repository"]["html_url"]
        markdown_text += f"## [{repo}]({repo_url})\n\n"
        for notification in notifications:
            notification_title = notification["subject"]["title"]
            notification_url = notification["subject"].get("url")
            if notification_url:
                notification_url = (
                    notification_url.replace("api.", "")
                    .replace("/repos", "")
                    .replace("pulls", "pull")
                )
                markdown_text += f"- [{notification_title}]({notification_url})\n"
            else:
                markdown_text += f"- {notification_title} (No URL available)\n"
        markdown_text += "\n"
    return markdown_text


def mark_notifications_as_read(token, notifications):
    headers = {"Authorization": f"token {token}"}
    for notification in notifications:
        notification_id = notification["id"]
        url = f"https://api.github.com/notifications/threads/{notification_id}"
        response = requests.patch(url, headers=headers)
        if response.status_code != 205:
            logging.error(
                f"Failed to mark notification {notification_id} as read. Status code: {response.status_code}"
            )


def main(
    since_date: datetime, github_token: str, target_project_ids, email_auth, email_to
):
    if target_project_ids:
        target_project_ids = [int(id) for id in target_project_ids.split(",")]

    notifications = get_github_notifications(
        since_date, github_token, repo_ids=target_project_ids
    )
    grouped_notifications = group_notifications_by_repo(notifications)
    formatted_text = format_notifications(grouped_notifications)

    print(formatted_text)

    if email_auth:
        subject_formatted = f"GitHub Digest {since_date.strftime('%m/%d/%Y')}-{datetime.now().strftime('%m/%d/%Y')}"

        send_email_markdown(
            markdown_content=formatted_text,
            subject=subject_formatted,
            email_auth=email_auth,
            email_to=email_to,
        )


if __name__ == "__main__":
    main()
