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


def test_single_case(t):
    # Run
    input = "../testcases/%d.in" % t
    answer = "../testcases/%d.ans" % t
    with open(input) as f:
        inputLines = "".join(f.readlines())
    with open(answer) as f:
        ansLines = f.readlines()

    cmd = "docker run -i -v /home/mkdong/code/QBoggle/canvas-autograder/docker/app:/app -w /app ubuntu:19.10 ./boggle.exe"
    try:
        proc = subprocess.run(cmd.split(),
                input=inputLines, text=True,
                capture_output=True,
                shell=False,
                timeout = 6)
        if proc.returncode == 0:
            # normal
            outLines = str(proc.stdout).split("\n")
            passed = True
            for i in range(len(ansLines)):
                outLines[i] = outLines[i].strip()
                ansLines[i] = ansLines[i].strip()
                if ("is too short." in ansLines[i] or
                        "is not a word." in ansLines[i] or
                        "is not on board." in ansLines[i] or
                        "is already found." in ansLines[i]):
                    outLines[i] = str.lower(outLines[i])
                    ansLines[i] = str.lower(ansLines[i])
                if outLines[i] != ansLines[i]:
                    # print(outLines)
                    if len(outLines[i]) > 20: outLines[i] = outLines[i][:20] + "..."
                    if len(ansLines[i]) > 20: ansLines[i] = ansLines[i][:20] + "..."
                    prompt = " Test #%d: Fail on Line %d (got \"%s\", expect \"%s\")\n" 
                    msg = prompt % (t, i, outLines[i], ansLines[i])
                    return (False, msg)
            return (True, " Test #%d: Passed.\n" % t)
        else:
            msg = " Test #%d: Runtime Exception %s\n" % (t, proc.stderr)
            return (False, msg)
    except subprocess.TimeoutExpired as e:
        print(e)
        return (False, " Test #%d: Timeout\n" % t)
    except UnicodeDecodeError as e:
        print(e)
        return (False, " Test #%d: Output Error\n" % t)

def calc_score(nr_passed, nr_total):
    if nr_passed == 0: return 40
    return 60 + 40 * nr_passed / nr_total

def update_score(sub, score, comment):
    """ [UNTESTED] Update the score of a submission.
    """
    sub.edit(submission={'posted_grade':score}, comment={'text_comment':comment})

idx = 0

for sub in lab5.get_submissions(bucket="ungraded", workflow_state="submitted"):
    idx += 1
    print(idx, sub.workflow_state)
    if sub.workflow_state == "submitted":
        attachments = sub.attachments
        # Find latest submission
        att = get_latest_attachment(attachments)
        url = att['url']
        fn = "boggle.cpp"
        if not os.path.exists(TEST_DIR):
            os.mkdir(TEST_DIR)
        fn = TEST_DIR + "/" + fn

        os.system("rm -f %s/*.cpp" % TEST_DIR)
        os.system("rm -f ./docker/app/boggle.exe")

        print(url, "=>", fn)
        urllib.request.urlretrieve(url, fn)

        message = ""
        cmd = "g++ -std=c++14 -o ./docker/app/boggle.exe ./testspace/boggle.cpp ../lexicon.cpp -I.."
        proc = subprocess.run(cmd.split(), capture_output=True)
        nr_passed = 0

        if proc.returncode == 0:
            message += "Compilation: Passed.\n"

            for t in range(1, 11):
                print("Testing case %d" % t)
                result, msg = test_single_case(t)
                if result:
                    nr_passed += 1
                message += msg
        else:
            message += "Compilation: Failed.\n"
            message += "Error message: " + str(proc.stderr)

        print(message)
        score = calc_score(nr_passed, 10)
        print("Score: %d" % score)

        update_score(sub, score, message)
        print("Score uploaded for %d" % sub.user_id)
        # break

        cmd = "sudo docker ps -a | cut -d ' ' -f 1 | xargs sudo docker kill >/dev/null 2>&1"
        os.system(cmd)

        cmd = "sudo docker ps -a | cut -d ' ' -f 1 | xargs sudo docker rm"
        os.system(cmd)


