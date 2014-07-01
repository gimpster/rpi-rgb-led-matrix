import ConfigParser
from job import Job
import jobstatus
import json
import sys
import time

settings = ConfigParser.ConfigParser()
settings.read(['jenkins.ini'])

QUERY_INTERVAL_SEC = int(settings.get('Global', 'QUERY_INTERVAL_SEC'))
JENKINS_JOB_LIST = []

for section in settings.sections():
    if 'Global' != section:
        if settings.has_option(section, 'USERNAME'):
            username = settings.get(section, 'USERNAME')
        else:
            username = None

        if settings.has_option(section, 'PASSWORD'):
            password = settings.get(section, 'PASSWORD')
        else:
            password = None

        base_url = settings.get(section, 'BASE_URL')
        json_url = settings.get(section, 'JSON_URL')
        job_list = json.loads(settings.get(section, 'JOB_LIST'))
        for job in job_list:
            JENKINS_JOB_LIST.append(Job(job, base_url + json_url % job, username, password))


def main():
    job_status = jobstatus.JobStatus(JENKINS_JOB_LIST)
    while True:
        job_status.run()
        time.sleep(QUERY_INTERVAL_SEC)


if __name__ == '__main__':
    sys.exit(main())