class Job():
    def __init__(self, name, url, username, password):
        self.name = name
        self.url = url
        self.username = username
        self.password = password
        self.status = 'NOT_BUILT'
