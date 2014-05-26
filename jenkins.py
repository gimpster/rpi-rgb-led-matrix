import requests
import os
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import sys
import thread
import time


JENKINS_BASE_URL = 'https://my.jenkins-ci.org'
JENKINS_JSON_URL = JENKINS_BASE_URL + '/job/%s/lastBuild/api/json'
JENKINS_USERNAME = 'authenticated_user'
JENKINS_PASSWORD = 'authenticated_password'
JENKINS_JOB_LIST = ['job1', 'job2']


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


class Switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:  # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


class LedStatus:
    def __init__(self, text=(("Raspberry Pi ", (255, 0, 0))), bgcolor='black'):
        font = ImageFont.truetype(os.path.dirname(os.path.realpath(__file__)) + '/C&C Red Alert [INET].ttf', 14)
        # font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 16)
        all_text = ''
        for text_color_pair in text:
            t = text_color_pair[0]
            all_text += t + ' '

        # print(all_text)
        width, ignore = font.getsize(all_text)
        # print(width)

        img = Image.new('RGB', (width + 32, 16), bgcolor)
        draw = ImageDraw.Draw(img)

        x = 0
        for text_color_pair in text:
            t = text_color_pair[0]
            c = text_color_pair[1]
            # print('t=' + t + ' ' + str(c) + ' ' + str(x))
            draw.text((x, 2), t, c, font=font)
            x = x + font.getsize(t)[0]

        img.save('status.ppm')

    @staticmethod
    def display():
        os.system("./led-matrix 1 status.ppm")
        # print 'Done.'


def print_culprits():
    out = ''
    if isinstance(culprits, basestring):
        return culprits
    else:
        if len(culprits) > 0:
            out = '(%s' % culprits[0]
            for i in range(1, len(culprits)):
                out += ', %s' % culprits[i]
            out += ')'
        return out


def format_culprits(culprits_):
    return print_culprits() if (result != 'SUCCESS' and len(culprits_) > 0) else ''


def format_job_status(job_, color_, result_, culprits_):
    return '%s: %s%s%s %s' % (job_, color_, result_, BColors.ENDC, format_culprits(culprits_))


def format_job_culprits(job_, culprits_):
    return '%s %s' % (job_, format_culprits(culprits_))


def passed():
    print 'ALL IS GOOD'
    text = [('ALL IS GOOD: ', (0, 0, 0)), ('%s PASSING JOBS' % len(passJobs), (0, 0, 0))]
    LedStatus(text, 'green').display()


def warned():
    print 'A DISTURBANCE IN THE FORCE'
    text = [('A DISTURBANCE IN THE FORCE: ', (0, 0, 0)), (warnJobs[0], (0, 0, 0))]
    warnJobs.pop(0)
    for warnJob in warnJobs:
        text.append((', %s' % warnJob, (0, 0, 0)))
    LedStatus(text, 'gold').display()


def failed():
    print 'RED ALERT!!'
    text = [('RED ALERT!! ', (0, 0, 0)), (failJobs[0], (0, 0, 0))]
    failJobs.pop(0)
    for failJob in failJobs:
        text.append((', %s' % failJob, (0, 0, 0)))
    LedStatus(text, 'red').display()


def initiated():
    print 'RETICULATING SPLINES'
    text = [('RETICULATING SPLINES: ', (0, 0, 0)), (initJobs[0], (0, 0, 0))]
    initJobs.pop(0)
    for initJob in initJobs:
        text.append((', %s' % initJob, (0, 0, 0)))
    LedStatus(text, 'blue').display()


passJobs = []
warnJobs = []
failJobs = []
initJobs = []

print 'Checking Jenkins...'
LedStatus([('Checking Jenkins...', (255, 0, 0))], 'black').display()
for job in JENKINS_JOB_LIST:
    color = ''
    culprits = []
    try:
        r = requests.get(JENKINS_JSON_URL % job, auth=(JENKINS_USERNAME, JENKINS_PASSWORD))
        if 200 <= r.status_code < 300:
            data = r.json()

            for culprit in data['culprits']:
                culprits.append(culprit['fullName'])

            result = 'BUILDING' if data['building'] else data['result']
            for case in Switch(result):
                if case('SUCCESS'):
                    color = BColors.OKGREEN
                    passJobs.append(format_job_culprits(job, culprits))
                    break
                if case('UNSTABLE', 'ABORTED', 'NOT_BUILT'):
                    color = BColors.WARNING
                    warnJobs.append(format_job_culprits(job, culprits))
                    break
                if case('FAILURE'):
                    color = BColors.FAIL
                    failJobs.append(format_job_culprits(job, culprits))
                    break
                if case('BUILDING'):
                    color = BColors.OKBLUE
                    initJobs.append(format_job_culprits(job, culprits))
                if case():
                    color = BColors.FAIL

            print format_job_status(job, color, result, culprits)
        else:
            culprits = [r.status_code]
            result = 'Invalid HTTP status code'
            color = BColors.FAIL
    except IOError, e:
        print e.message
    except StopIteration, e:
        print e.message

if len(failJobs) > 0:
    failed()
else:
    if len(warnJobs) > 0:
        warned()
    else:
        if len(initJobs) > 0:
            initiated()
        else:
            passed()