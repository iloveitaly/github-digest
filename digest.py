import os
import requests
from datetime import datetime, timedelta
from collections import defaultdict


def get_github_notifications(since="1w", repo_ids=None):
    token = os.getenv("GITHUB_TOKEN")
    since_date = (
        datetime.utcnow() - timedelta(weeks=1 if since == "1w" else int(since[:-1]))
    ).isoformat()
    url = f"https://api.github.com/notifications?since={since_date}"
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


# Usage
target_project_ids = os.getenv("TARGET_PROJECT_IDS")
if target_project_ids:
    target_project_ids = [int(id) for id in target_project_ids.split(",")]
notifications = get_github_notifications(repo_ids=target_project_ids)
grouped_notifications = group_notifications_by_repo(notifications)
formatted_text = format_notifications(grouped_notifications)
print(formatted_text)
