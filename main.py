#!/usr/bin/env python3

"""
git-svn-sync: a server that reflects commits made on GitHub repos to
svn repos.

Sai Vineet(svineet) saivineet89@gmail.com
"""

import json
import os
import subprocess
import http.server
import socketserver

from pprint import pprint
from config import PORT, DIRECTORY_MAP
from config import INITIAL_COMMIT_MESSAGE, COMMIT_MESSAGE


def do_command(command):
    command = subprocess.check_output(command,
                                      shell=True)
    print(command.decode('utf-8'))


def svn_clone(repo_name):
    name, git_url, svn_url = DIRECTORY_MAP[repo_name]
    initial_dir = os.getcwd()
    dir_ = os.path.join(os.getcwd(), name)
    try:
        do_command('svn co "'+svn_url+'" "'+name+'"')
        print('Cloned from SVN successfully.')

        print('Initializing local repo and setting remotes to GitHub')

        os.chdir(dir_)
        do_command('git init')
        do_command('git remote add origin '+git_url)
        do_command('git fetch origin master')
        do_command('git reset --hard origin/master')

        print('Setting ignores for svn')
        do_command('svn propset svn:ignore .git .')

        os.chdir(initial_dir)
    except subprocess.CalledProcessError:
        print('error :(')


def svn_push(repo_name, data):
    dir_name, git_url, svn_url = DIRECTORY_MAP[repo_name]

    if not data:
        try:
            do_command('svn add --force .')
            do_command('svn commit -m "'+INITIAL_COMMIT_MESSAGE+'"')
        except subprocess.CalledProcessError:
            print('error :(')

        return

    email, name = data['pusher']['email'], data['pusher']['name']
    msg = data['head_commit']['message']
    commit_message = COMMIT_MESSAGE.format(
        msg, name, email)
    print('Commiting with message '+commit_message)

    try:
        do_command('svn add --force .')
        do_command('svn commit -m "'+commit_message+'" --no-unlock')
    except subprocess.CalledProcessError:
        print('error :(')


def git_pull(repo_name, data={}):
    initial_dir = os.getcwd()
    dir_ = os.path.join(os.getcwd(), DIRECTORY_MAP[repo_name][0])

    if not os.path.isdir(dir_):
        print('Could not find repo '+repo_name+', now cloning.')
        svn_clone(repo_name)
        os.chdir(dir_)
        svn_push(repo_name, data)
        os.chdir(initial_dir)
        return

    os.chdir(dir_)
    try:
        do_command('git pull origin master')
        svn_push(repo_name, data)
    except subprocess.CalledProcessError:
        print('error :(')
    os.chdir(initial_dir)


class SyncHandler(http.server.SimpleHTTPRequestHandler):
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

        # handle GitHub triggers only
        if 'GitHub' in self.headers['User-Agent']:
            # pprint(data)
            event = self.headers['X-Github-Event']
            email, name = data['pusher']['email'], data['pusher']['name']
            repo = data['repository']['name']

            print("{}: {} committed to {}".format(name, email, repo))

            if event == 'push':
                git_pull(repo, data)

        self.send_response(200)


if __name__ == '__main__':
    print('Pulling all repositories')
    print('-'*80)
    for (key, value) in DIRECTORY_MAP.items():
        print('Pulling: '+key)
        git_pull(key)

    httpd = socketserver.TCPServer(("", PORT), SyncHandler)
    print("Serving on {}".format(PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print()
        print('Exiting')
