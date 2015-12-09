"""
Artorias: a server that reflects commits made on GitHub repos to
svn repos.

svineet saivineet89@gmail.com
"""

import json
import os
import subprocess
import http.server
import socketserver

from pprint import pprint
from config import PORT, DIRECTORY_MAP


def git_pull(repo_name):
    initial_dir = os.getcwd()
    dir_ = os.path.join(os.getcwd(), DIRECTORY_MAP[repo_name])
    os.chdir(dir_)

    try:
        command = subprocess.check_output('git pull origin master',
                                          shell=True)
        print('Git output:')
        print('-'*80)
        print(command.decode('utf-8'))
        print('-'*80)
    except subprocess.CalledProcessError:
        print('error :(')
    os.chdir(initial_dir)


class Artorias(http.server.SimpleHTTPRequestHandler):
    """
        HTTP Server that syncs local svn repos with upstream
        GitHub repos.
    """
    def do_GET(self):
        '''Returns an error because GET is useless for us'''
        self.send_response(403)

    def do_POST(self):
        '''Handles POST requests for all hooks.'''

        # read and decode data
        length = int(self.headers['Content-Length'])
        indata = self.rfile.read(length)
        data = json.loads(indata.decode('utf-8'))

        # pprint(data)

        # handle GitHub triggers only
        if 'GitHub' in self.headers['User-Agent']:
            event = self.headers['X-Github-Event']
            email, name = data['pusher']['email'], data['pusher']['name']
            repo = data['repository']['name']

            print("{}: {} committed to {}".format(name, email, repo))

            if event == 'push':
                git_pull(repo)

        self.send_response(200)


if __name__ == '__main__':
    print('Pulling all repositories')
    print('-'*80)
    for (key, value) in DIRECTORY_MAP.items():
        print('Pulling: '+key)
        git_pull(key)

    httpd = socketserver.TCPServer(("", PORT), Artorias)
    print("Serving on {}".format(PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print()
        print('Exiting')
