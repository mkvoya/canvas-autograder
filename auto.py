#!/bin/python3

import sys
import os
from datetime import *
import urllib
import subprocess

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
        fn = TEST_DIR + "/" + fn

        os.system("rm -f %s/*.msg" % TEST_DIR)
        os.system("rm -f %s" % fn)

        print(url, "=>", fn)
        urllib.request.urlretrieve(url, fn)

        message = ""
        cmd = "g++ -std=c++17 -o ./testspace/boggle.exe ./testspace/boggle.cpp ../lexicon.cpp -I.."
        proc = subprocess.run(cmd.split(), capture_output=True)
        if proc.returncode == 0:
            message += "Compilation: Passed.\n"
        else:
            message += "Compilation: Failed.\n"
            message += "Error message: " + str(proc.stderr)

        nr_passed = 0
        for t in range(1, 11):
            # Run
            cmd = "./testspace/boggle.exe"
            input = "../testcases/%d.in" % t
            answer = "../testcases/%d.ans" % t

            with open(input) as f:
                inputBytes = "".join(f.readlines())
            with open(answer) as f:
                ansLines = f.readlines()
            proc = subprocess.run(["./testspace/boggle.exe"],
                    input=inputBytes, text=True,
                    capture_output=True,
                    timeout = 5)
            if proc.returncode == 0:
                # normal
                outLines = str(proc.stdout).split("\n")
                passed = True
                for i in range(len(ansLines)):
                    outLines[i] = outLines[i].strip()
                    ansLines[i] = ansLines[i].strip()
                    if outLines[i] != ansLines[i]:
                        # print(outLines)
                        prompt = " Test #%d: Fail on Line %d (got \"%s\", expect \"%s\")\n" 
                        message += prompt % (t, i, outLines[i], ansLines[i])
                        passed = False
                        break
                if passed:
                    message += " Test #%d: Passed.\n" % t
                    nr_passed += 1
            else:
                message += " Test #%d: Exception or Timeout\n" % t
        print(message)

        # os.system("bash test.sh")
        print(sub.user_id)
        # break


def calc_score(nr_passed, nr_total):
    if nr_passed == 0: return 40
    return 60 + 40 * nr_passed / nr_total

def update_score(sub, score):
    """ [UNTESTED] Update the score of a submission.
    """
    sub.edit(submission={'posted_grade':score})

