from bcolors import BColors
# from enum import Enum
from ledstatus import LedStatus
import requests
from switch import Switch


# class Status(Enum):
# SUCCESS = 1
# BUILDING = 2
#     UNSTABLE = 3
#     ABORTED = 4
#     NOT_BUILT = 5
#     FAILURE = 6


class JobStatus():
    def __init__(self, jenkins_username, jenkins_password, jenkins_job_list):
        self.jenkins_username = jenkins_username
        self.jenkins_password = jenkins_password
        self.jenkins_job_list = jenkins_job_list

        self.pass_jobs = []
        self.warn_jobs = []
        self.fail_jobs = []
        self.init_jobs = []
        self.led_status = LedStatus()
        # self.status = Enum('Status', 'SUCCESS BUILDING UNSTABLE ABORTED NOT_BUILT FAILURE')

    def __call__(self):
        self.run()

    def check_status(self):
        self.pass_jobs = []
        self.warn_jobs = []
        self.fail_jobs = []
        self.init_jobs = []

        print 'Checking Jenkins...'
        self.led_status.set_status([('Checking Jenkins...', (255, 0, 0))], 'white')
        self.led_status.display()

        for job in self.jenkins_job_list:
            self.get_job_status(job)

        if len(self.fail_jobs) > 0:
            self.display_status('RED ALERT', self.fail_jobs, 'red')
        elif len(self.warn_jobs) > 0:
            self.display_status('A DISTURBANCE IN THE FORCE', self.warn_jobs, 'gold')
        elif len(self.init_jobs) > 0:
            self.display_status('RETICULATING SPLINES', self.init_jobs, 'blue')
        else:
            self.display_status('ALL IS GOOD', [('%s PASSING JOBS' % len(self.pass_jobs))], 'green')

    def display_status(self, status_message='', job_list=list(), bgcolor='black'):
        print status_message
        text = [('%s: ' % status_message, (0, 0, 0))]
        text.extend(JobStatus.format_job_color_tuple(job_list))
        self.led_status.set_status(text, bgcolor)
        self.led_status.display()

    @staticmethod
    def format_culprits(result, culprits):
        return JobStatus.print_culprits(culprits) if (result != 'SUCCESS' and len(culprits) > 0) else ''

    @staticmethod
    def format_job_color_tuple(job_list=list(), font_color=(0, 0, 0)):
        if not isinstance(job_list, basestring) & len(job_list) > 0:
            formatted_text = [(job_list[0], font_color)]
            job_list.pop(0)
            for job in job_list:
                formatted_text.append((', %s' % job, font_color))
        else:
            formatted_text = [(job_list, font_color)]

        return formatted_text

    @staticmethod
    def format_job_culprits(job, result, culprits):
        return '%s %s' % (job, JobStatus.format_culprits(result, culprits))

    @staticmethod
    def format_job_status(job, color, result, culprits):
        return '%s: %s%s%s %s' % (job, color, result, BColors.ENDC, JobStatus.format_culprits(result, culprits))

    def get_job_status(self, job):
        culprits = []
        color = ''

        try:
            r = requests.get(job, auth=(self.jenkins_username, self.jenkins_password), verify=False)
            if 200 <= r.status_code < 300:
                data = r.json()

                for culprit in data['culprits']:
                    culprits.append(culprit['fullName'])

                result = 'BUILDING' if data['building'] else data['result']
                for case in Switch(result):
                    if case('SUCCESS'):
                        color = BColors.OKGREEN
                        self.pass_jobs.append(JobStatus.format_job_culprits(job, result, culprits))
                        break
                    if case('UNSTABLE', 'ABORTED', 'NOT_BUILT'):
                        color = BColors.WARNING
                        self.warn_jobs.append(JobStatus.format_job_culprits(job, result, culprits))
                        break
                    if case('FAILURE'):
                        color = BColors.FAIL
                        self.fail_jobs.append(JobStatus.format_job_culprits(job, result, culprits))
                        break
                    if case('BUILDING'):
                        color = BColors.OKBLUE
                        self.init_jobs.append(JobStatus.format_job_culprits(job, result, culprits))
                    if case():
                        color = BColors.FAIL
            else:
                culprits = [r.status_code]
                result = 'Invalid HTTP status'
                color = BColors.FAIL

            print JobStatus.format_job_status(job, color, result, culprits)
        except IOError, e:
            print e.message
        except StopIteration, e:
            print e.message

    @staticmethod
    def print_culprits(culprits):
        out = ''
        if isinstance(culprits, basestring):
            return culprits
        else:
            if len(culprits) > 0:
                out = '(%s' % culprits[0]
                culprits.pop(0)
                for culprit in culprits:
                    out += ', %s' % culprit
                out += ')'
            return out

    def run(self):
        self.check_status()
