import logging
import os
import re
import time

import praw
import prawcore

import posts as db

logging.basicConfig(level=logging.INFO)

# variables
user_regex = r"/?[Uu]/([A-Za-z0-9_-]+)"
multiple_mentions_regex = r"([^\w-][Xx] ?\d+)|([^\w/-]\d+ ?[Xx])|(^[Xx] ?\d+)|(^\d+ ?[Xx])"
mystery_list = ["mystery user", "mystery sender"]

RUNNING_IN_DOCKER = os.environ.get('RUNNING_IN_DOCKER', False)
USE_PROXY = os.environ.get('USE_PROXY', False)

# RAoC bot
client_id = os.environ.get('REDDIT_BOT_CLIENT_ID')
client_secret = os.environ.get('REDDIT_BOT_CLIENT_SECRET')
username = os.environ.get('REDDIT_BOT_USERNAME')
password = os.environ.get('REDDIT_BOT_PASSWORD')
user_agent = "python:raoc_bot:v0.0.1 (by u/catshapednoodles)"

if not client_id:
    exit("RAOCFlair bot could not start: REDDIT_BOT_CLIENT_ID not provided")
if not client_secret:
    exit("RAOCFlair bot could not start: REDDIT_BOT_CLIENT_SECRET not provided")
if not username:
    exit("RAOCFlair bot could not start: REDDIT_BOT_USERNAME not provided")
if not password:
    exit("RAOCFlair bot could not start: REDDIT_BOT_PASSWORD not provided")

# creating an authorized reddit instance
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     username=username,
                     password=password,
                     user_agent=user_agent)

# to find the top most submission in the subreddit "RandomActsofCards"
subreddit = reddit.subreddit('RandomActsofCards')


def get_usernames_from_selftext(selftext: str):
    logging.debug("Getting usernames from selftext")
    pattern = re.compile(user_regex)
    usernames = []
    for match in pattern.finditer(selftext):
        usernames.append(match.group(1))
    return usernames


def get_usernames_from_comments(comments):
    logging.debug("Getting usernames from comments")
    users_in_comments = []
    pattern = re.compile(user_regex)
    for comment in comments:
        for match in pattern.finditer(comment.body):
            users_in_comments.append(match.group(1))
    return users_in_comments


def get_multiple_mentions_from_selftext(selftext):
    logging.debug("Checking if there are multiple mentions in selftext")
    pattern = re.compile(multiple_mentions_regex)
    result = pattern.findall(selftext)
    if result:
        return True
    else:
        return False


def get_unique_users(user_list: list):
    logging.debug("Getting all unique users")
    unique_list = []
    for user in user_list:
        if user.casefold() not in map(str.casefold, unique_list):
            unique_list.append(user)
    return unique_list


def get_roacflair_posts(user_list: list):
    logging.debug("Getting the newest post on raocflair for all users")
    flair_list = []
    for user in user_list:
        flair_post_found = False
        roacflair_url = ""

        for submission in reddit.subreddit("RAOCFlair").search(user, sort="new"):
            if user.casefold() in submission.title.casefold():
                roacflair_url = submission.url
                flair_post_found = True
                break

        if flair_post_found:
            flair_list.append([user, roacflair_url])
        else:
            flair_list.append([user, ""])

    return flair_list


def process_submission(submission):
    logging.debug("Processing a new submission")
    flair = submission.link_flair_text
    if flair == "Thank You":
        logging.debug("New submission is a [Thank You] post, processing further")
        post_id = submission.id
        if db.check_if_post_in_database(post_id):
            return

        mentioned_users = []
        multiple_mentions = False
        logging.info(f"Processing new Thank You post {submission.url}")

        mentioned_users.extend(get_usernames_from_selftext(submission.selftext))

        unique_list = get_unique_users(mentioned_users)
        if len(mentioned_users) != len(unique_list):
            multiple_mentions = True
        elif get_multiple_mentions_from_selftext(submission.selftext):
            multiple_mentions = True

        unique_list.extend(get_usernames_from_selftext(submission.title))
        unique_list = get_unique_users(unique_list)

        mystery_user = False
        for string in mystery_list:
            if string in submission.selftext.lower():
                mystery_user = True

        raocflair_list = get_roacflair_posts(unique_list)

        author = submission.author.name
        title = submission.title
        url = submission.url
        timestamp = submission.created_utc

        return db.insert_to_db(post_id=post_id, author=author, title=title, url=url, timestamp=timestamp,
                               mentioned_users_post=raocflair_list, mystery_user=mystery_user,
                               multiple_mentions=multiple_mentions)


def catch_submissions():
    logging.debug("Starting the subreddit submission stream")
    for submission in subreddit.stream.submissions():
        process_submission(submission)


if __name__ == '__main__':
    db.create_database_and_tables()
    logging.info("Starting RAOCFlair bot")
    while True:
        try:
            catch_submissions()
        except prawcore.exceptions.RequestException as e:
            logging.exception('An exception occurred')
            logging.info("Retrying in 1 minute...")
            time.sleep(60)
        except Exception as e:
            logging.exception('An exception occurred')
            logging.info("Retrying in 1 minute...")
            time.sleep(60)
