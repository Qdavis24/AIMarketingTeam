import os
from dotenv import load_dotenv
import praw
import time
import json
load_dotenv()

ua = f"Yellowstone Expedition Guide (by /u/{os.getenv("R_UN")}"
reddit = praw.Reddit(client_id=os.getenv("R_CI"), client_secret=os.getenv("R_SECRET"),
                     user_agent=ua, username=os.getenv("R_UN"), password=os.getenv("R_PW"))


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
    return len(curr_posts)

def read() -> dict:
    with open("./posts.json", "r") as file:
        all_posts = json.loads(file.read())
    one_post = all_posts.pop()
    with open("./posts.json", "w") as file:
        json.dump(all_posts, file)
    return one_post  


def search(keyword: str) -> json:
    results = reddit.subreddit("all").search(keyword, limit=3, time_filter="day")
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
