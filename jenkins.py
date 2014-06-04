import jobstatus
import sys
import time

settings = ConfigParser.ConfigParser()
settings.read(['jenkins.ini'])

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
    global passJobs
    global warnJobs
    global failJobs
    global initJobs
    job_status = jobstatus.JobStatus(JENKINS_USERNAME, JENKINS_PASSWORD, JENKINS_JOB_LIST)
    while True:
        passJobs = []
        warnJobs = []
        failJobs = []
        initJobs = []

        job_status.run()
        time.sleep(QUERY_INTERVAL_SEC)


if __name__ == '__main__':
    sys.exit(main())