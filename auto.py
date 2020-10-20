#!/bin/python3

import sys
import os
from datetime import *
import urllib

# Import the Canvas class
from canvasapi import Canvas

# Canvas API URL
API_URL = "https://oc.sjtu.edu.cn"
# Canvas API key
API_KEY = "NOKEY"
if os.path.exists("local.key"):
    with open("local.key") as f:
        API_KEY = f.readlines()[0]
else:
    API_KEY = input("Please Input Your API Key:")

# SEP Course
SEP_COURSE_ID = 24561
LAB3_ASSIGNMENT_ID = 67644
SUBMISSION_DIR = "./submissions"

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)
course = canvas.get_course(SEP_COURSE_ID)
print(course)

lab3 = course.get_assignment(LAB3_ASSIGNMENT_ID)
print(lab3)

def get_latest_attachment(attachments):
    """ [UNTESTED] Get the latest attachment since a user may submit multiple times.
    """
    all_attachments = []
    for att in attachments:
        all_attachments.append((datetime.fromisoformat(att['created_at'][:-1]), att))
    att = sorted(all_attachments)[-1][1]
    return att

for sub in lab3.get_submissions(bucket="ungraded", workflow_state="submitted"):
    if sub.workflow_state == "submitted":
        attachments = sub.attachments
        # Find latest submission
        att = get_latest_attachment(attachments)
        url = att['url']
        fn = att['filename']
        if not os.path.exists(SUBMISSION_DIR):
            os.mkdir(SUBMISSION_DIR)
        fn = SUBMISSION_DIR + "/" + fn

        print(url, "=>", fn)
        urllib.request.urlretrieve(url, fn)


def update_score(sub, score):
    """ [UNTESTED] Update the score of a submission.
    """
    sub.edit(submission={'posted_grade':score})

