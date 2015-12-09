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


class Artorias(http.server.SimpleHTTPRequestHandler):

    # return error code because a GET request is meaningless
    def do_GET(self):
        print('Gott')
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
                self.git_pull(data)

        self.send_response(200)

    def git_pull(self, data):
        repo = data['repository']['name']
        initial_dir = os.getcwd()
        dir_ = os.path.join(os.getcwd(), DIRECTORY_MAP[repo])
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


if __name__ == '__main__':
    httpd = socketserver.TCPServer(("", PORT), Artorias)
    print("Serving on {}".format(PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print()
        print('Exiting')
