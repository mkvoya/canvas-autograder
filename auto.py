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
LAB4_ASSIGNMENT_ID = 69983
LAB5_ASSIGNMENT_ID = 73568
SUBMISSION_DIR = "./submissions"
TEST_DIR = "./testspace"

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)
course = canvas.get_course(SEP_COURSE_ID)
print(course)

# lab3 = course.get_assignment(LAB3_ASSIGNMENT_ID)
# print(lab3)
# lab4 = course.get_assignment(LAB4_ASSIGNMENT_ID)
# print(lab4)

lab5 = course.get_assignment(LAB5_ASSIGNMENT_ID)
print(lab5)

def get_latest_attachment(attachments):
    """ [UNTESTED] Get the latest attachment since a user may submit multiple times.
    """
    all_attachments = []
    for att in attachments:
        all_attachments.append((datetime.fromisoformat(att['created_at'][:-1]), att))
    att = sorted(all_attachments)[-1][1]
    return att

for sub in lab5.get_submissions(bucket="ungraded", workflow_state="submitted"):
    print(sub.workflow_state)
    if sub.workflow_state == "submitted":
        attachments = sub.attachments
        # Find latest submission
        att = get_latest_attachment(attachments)
        url = att['url']
        fn = att['filename']
        if not os.path.exists(TEST_DIR):
            os.mkdir(TEST_DIR)
            os.system("cp ../lexicon.cpp %s/" % TEST_DIR)
            os.system("cp ../lexicon.h %s/" % TEST_DIR)
            os.system("cp ../EnglishWords.txt %s/" % TEST_DIR)
        fn = TEST_DIR + "/" + fn

        os.system("rm -f %s" % fn)

        print(url, "=>", fn)
        urllib.request.urlretrieve(url, fn)

        os.system("bash test.sh")
        print(sub.user_id)
        break


def calc_score(nr_passed, nr_total):
    if nr_passed == 0: return 40
    return 60 + 40 * nr_passed / nr_total

def update_score(sub, score):
    """ [UNTESTED] Update the score of a submission.
    """
    sub.edit(submission={'posted_grade':score})


def test_a_single_submission(uri):
    cmd = "g++ -o boggle.exe -std=c++17 boggle.c lexicon.c"
    os.system(cmd)
    test_in_file
    def test_(inF, ouF, anF):
        cmd = "./boggle.exe < %s > %s" % (inF, ouF)
        os.system(cmd)
        cmd = "diff %s %s" % (anF, ouF)
    for y in range(10):
        i = y + 1
        test_("%d.in" % i, "%d.out" % i, "%d.ans" % i)

