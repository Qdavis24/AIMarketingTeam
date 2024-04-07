import os
import praw
import time
import json

ua = f"Yellowstone Expedition Guide (by /u/{os.environ.get("R_UN")}"
reddit = praw.Reddit(client_id=os.environ.get("R_CI"), client_secret=os.environ.get("R_SECRET"),
                     user_agent=ua, username=os.environ.get("R_UN"), password=os.environ.get("R_PW"))


def store(data: list) -> list:
    try:
        with open("./posts.json", "r") as file:
            curr_posts = json.loads(file.read())
    except FileNotFoundError:
        curr_posts = data
        with open("./posts.json", "w") as file:
            json.dump(curr_posts, file)
    else:
        duplicates = []
        curr_posts.extend(data)
        for index, post in enumerate(curr_posts):
            for i, p in enumerate(curr_posts):
                if post["post_id"] == p["post_id"] and index != i:
                    duplicates.append(i)
        for item in duplicates:
            del curr_posts[item]
        with open("./posts.json", "w") as file:
            json.dump(curr_posts, file)
    return curr_posts


def search(keyword: str) -> json:
    results = reddit.subreddit("all").search(keyword, limit=5)
    export = []
    for post in results:
        dict = {}
        if not post.locked and post.is_self and not post.archived:
            dict["title"] = post.title
            dict["post"] = post.selftext
            dict["post_id"] = post.id
            export.append(dict)
    return export


def reply(post_id: str, message: str) -> int:
    post = reddit.submission(post_id)
    post.reply(message)
    return post.permalink


def wait(duration: int) -> int:
    seconds = duration * 60
    time.sleep(seconds)
    return 1
