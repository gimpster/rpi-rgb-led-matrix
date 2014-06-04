import ConfigParser
import jobstatus
import json
import sys
import time

settings = ConfigParser.ConfigParser()
settings.read(['jenkins.ini'])

JENKINS_USERNAME = settings.get('Global', 'USERNAME')
JENKINS_PASSWORD = settings.get('Global', 'PASSWORD')
QUERY_INTERVAL_SEC = int(settings.get('Global', 'QUERY_INTERVAL_SEC'))
JENKINS_JOB_LIST = []

for section in settings.sections():
    if 'Global' != section:
        base_url = settings.get(section, 'BASE_URL')
        json_url = settings.get(section, 'JSON_URL')
        job_list = json.loads(settings.get(section, 'JOB_LIST'))
        for job in job_list:
            JENKINS_JOB_LIST.append(base_url + json_url % job)


def main():
    job_status = jobstatus.JobStatus(JENKINS_USERNAME, JENKINS_PASSWORD, JENKINS_JOB_LIST)
    while True:
        job_status.run()
        time.sleep(QUERY_INTERVAL_SEC)


if __name__ == '__main__':
    sys.exit(main())