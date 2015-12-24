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
from config import INITIAL_COMMIT_MESSAGE, COMMIT_MESSAGE, UPDATE_COMMIT_MESSAGE

UNLOCK_COMMAND = '''find . -type d \( -path ./.git -o -path ./.svn \) -prune -o -exec sh -c '../unlocker.sh "{}"' \;'''
LOCK_COMMAND = '''find . -type d \( -path ./.git -o -path ./.svn \) -prune -o -exec sh -c '../locker.sh "{}"' \;'''

def do_command(command, print_output=True, return_=False):
    """
        Execute a command on the shell and return output if asked for.
    """
    output = subprocess.check_output(command, stderr=subprocess.STDOUT,
                                     shell=True)
    if print_output:
        print(output.decode('utf-8'))

    if return_:
        return output.decode('utf-8')


def get_sha(repo_name):
    """
        Enters repo_name directory and returns current git sha
    """
    initial_dir = os.getcwd()
    dir_ = os.path.join(os.getcwd(), repo_name)

    os.chdir(dir_)
    shia = ""
    try:
        shia = do_command('git rev-parse HEAD', return_=True)
    except subprocess.CalledProcessError as error:
        print('error :(')
        print(error)
    os.chdir(initial_dir)

    return shia


def svn_clone(repo_name):
    """
        Enter repo_name directory and clone.
        Will sync local repo with git remote.
        Also does related things like add ignores and tries setting locks.
    """
    name, git_url, svn_url = DIRECTORY_MAP[repo_name]
    initial_dir = os.getcwd()
    dir_ = os.path.join(os.getcwd(), name)

    try:
        do_command('svn co "'+svn_url+'" "'+name+'"')
        print('Cloned from SVN successfully.')
        print('Setting ignores for svn')
        do_command('svn propset svn:ignore .git .')

        print('Initializing local repo and setting remotes to GitHub')
        os.chdir(dir_)
        do_command('git init')
        do_command('git remote add origin '+git_url)

        do_command('svn rm --force ./*')
        do_command('git fetch origin master')
        do_command('git reset --hard origin/master')
        do_command('svn add --force .')


        os.chdir(initial_dir)
    except subprocess.CalledProcessError as error:
        print('error :(')
        print(error)

    os.chdir(dir_)
    try:
        print('Now trying to gain lock access. May fail.')
        do_command(UNLOCK_COMMAND, print_output=True)
        do_command(LOCK_COMMAND, print_output=True)
        print('Locking might have worked.')
    except subprocess.CalledProcessError as error:
        print('Unlocking/locking failed. Please see README#Troubleshooting')
        print(error)
    os.chdir(initial_dir)


def svn_push(repo_name, commit_message):
    """
        Enter a directory with repo_name and then
        svn commit with commit message.
        It will first restore pristine state using git clean -d -f
        then it will remove all staged files from svn
        then it will add all files in current dir to svn
        then it pushes to remote svn. This is so that
        deleted or renamed files are taken care of.
    """
    dir_name, git_url, svn_url = DIRECTORY_MAP[repo_name]
    initial_dir = os.getcwd()
    dir_ = os.path.join(os.getcwd(), dir_name)

    print('Commiting with message '+commit_message)
    os.chdir(dir_)
    try:
        do_command('svn commit -m "'+commit_message+'" --no-unlock')
    except subprocess.CalledProcessError as error:
        print('error :(')
        print(error)

    os.chdir(initial_dir)


def git_pull(repo_name):
    """
        Enter repo_name directory and fetch-reset from git repo.

        It will also remove all files from svn tracking and then
        add them again to svn so that renamed files and deleted
        files are taken care of.
    """
    initial_dir = os.getcwd()
    dir_ = os.path.join(os.getcwd(), DIRECTORY_MAP[repo_name][0])

    os.chdir(dir_)
    try:
        do_command('svn rm --force ./*')
        do_command('git fetch origin master')
        do_command('git reset --hard origin/master')
        do_command('svn add --force .')
    except subprocess.CalledProcessError as error:
        print('error :(')
        print(error)
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
            event = self.headers['X-Github-Event']
            email, name = data['pusher']['email'], data['pusher']['name']
            repo = data['repository']['name']
            dir_ = DIRECTORY_MAP[repo][0]

            print("{}: {} committed to {}".format(name, email, repo))
            if event == 'push':
                git_pull(repo)
                new_sha = get_sha(repo)
                gh_msg = data['head_commit']['message']
                commit_message = COMMIT_MESSAGE.format(
                    gh_msg, new_sha[:7], name, email)
                svn_push(repo, commit_message)

        self.send_response(200)


if __name__ == '__main__':
    print('Pulling all repositories')
    print('-'*80)
    for (repo_name, value) in DIRECTORY_MAP.items():
        print('Pulling: '+repo_name)

        dir_ = os.path.join(os.getcwd(), DIRECTORY_MAP[repo_name][0])
        commit_message = INITIAL_COMMIT_MESSAGE
        if not os.path.isdir(dir_):
            print('Could not find repo '+repo_name+', now cloning.')
            svn_clone(repo_name)
        else:
            pre_sha = get_sha(repo_name)
            git_pull(repo_name)
            post_sha = get_sha(repo_name)
            commit_message = UPDATE_COMMIT_MESSAGE.format(repo_name, pre_sha, post_sha)

        svn_push(repo_name, commit_message)
        print('-'*80)

    httpd = socketserver.TCPServer(("", PORT), SyncHandler)
    print("Serving on {}".format(PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print()
        print('Exiting')
