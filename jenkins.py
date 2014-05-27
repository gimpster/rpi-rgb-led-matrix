from bcolors import BColors
from ledstatus import LedStatus
import requests
from switch import Switch
import sys
import thread
import time


JENKINS_BASE_URL = 'https://my.jenkins-ci.org'
JENKINS_JSON_URL = JENKINS_BASE_URL + '/job/%s/lastBuild/api/json'
JENKINS_USERNAME = 'authenticated_user'
JENKINS_PASSWORD = 'authenticated_password'
JENKINS_JOB_LIST = ['job1', 'job2']

passJobs = []
warnJobs = []
failJobs = []
initJobs = []
ledStatus = LedStatus()


def main():
    print 'Checking Jenkins...'
    ledStatus.set_status([('Checking Jenkins...', (255, 0, 0))], 'black')
    ledStatus.display()

    for job in JENKINS_JOB_LIST:
        culprits = []
        color = ''

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
                        passJobs.append(format_job_culprits(job, result, culprits))
                        break
                    if case('UNSTABLE', 'ABORTED', 'NOT_BUILT'):
                        color = BColors.WARNING
                        warnJobs.append(format_job_culprits(job, result, culprits))
                        break
                    if case('FAILURE'):
                        color = BColors.FAIL
                        failJobs.append(format_job_culprits(job, result, culprits))
                        break
                    if case('BUILDING'):
                        color = BColors.OKBLUE
                        initJobs.append(format_job_culprits(job, result, culprits))
                    if case():
                        color = BColors.FAIL
            else:
                culprits = [r.status_code]
                result = 'Invalid HTTP status'
                color = BColors.FAIL

            print format_job_status(job, color, result, culprits)
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


def print_culprits(culprits):
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


def format_culprits(result, culprits):
    return print_culprits(culprits) if (result != 'SUCCESS' and len(culprits) > 0) else ''


def format_job_status(job, color, result, culprits):
    return '%s: %s%s%s %s' % (job, color, result, BColors.ENDC, format_culprits(result, culprits))


def format_job_culprits(job, result, culprits):
    return '%s %s' % (job, format_culprits(result, culprits))


def passed():
    print 'ALL IS GOOD'
    text = [('ALL IS GOOD: ', (0, 0, 0)), ('%s PASSING JOBS' % len(passJobs), (0, 0, 0))]
    ledStatus.set_status(text, 'green')
    ledStatus.display()


def warned():
    print 'A DISTURBANCE IN THE FORCE'
    text = [('A DISTURBANCE IN THE FORCE: ', (0, 0, 0)), (warnJobs[0], (0, 0, 0))]
    warnJobs.pop(0)
    for warnJob in warnJobs:
        text.append((', %s' % warnJob, (0, 0, 0)))
    ledStatus.set_status(text, 'gold')
    ledStatus.display()


def failed():
    print 'RED ALERT!!'
    text = [('RED ALERT!! ', (0, 0, 0)), (failJobs[0], (0, 0, 0))]
    failJobs.pop(0)
    for failJob in failJobs:
        text.append((', %s' % failJob, (0, 0, 0)))
    ledStatus.set_status(text, 'red')
    ledStatus.display()


def initiated():
    print 'RETICULATING SPLINES'
    text = [('RETICULATING SPLINES: ', (0, 0, 0)), (initJobs[0], (0, 0, 0))]
    initJobs.pop(0)
    for initJob in initJobs:
        text.append((', %s' % initJob, (0, 0, 0)))
    ledStatus.set_status(text, 'blue')
    ledStatus.display()


if __name__ == '__main__':
    sys.exit(main())