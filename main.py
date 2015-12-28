#!/usr/bin/env python3

"""
git-svn-sync: a server that reflects commits made on GitHub repos to
svn repos.

Sai Vineet(svineet) saivineet89@gmail.com
"""

import sys
import json
import os
import subprocess
import http.server
import socketserver

from pprint import pprint
try:
    from config import PORT, DIRECTORY_MAP
except ImportError:
    print('Please copy config.example.py into config.py and edit as required')
    print('Exiting.')
    sys.exit(0)
from config import INITIAL_COMMIT_MESSAGE, COMMIT_MESSAGE, UPDATE_COMMIT_MESSAGE
from config import BREAK_LOCKS_EVERYTIME, RELOCK_EVERYTIME

UNLOCK_COMMAND = '''find . -type d \( -path ./.git -o -path ./.svn \) -prune -o -exec svn unlock --force {} \;'''
LOCK_COMMAND = '''find . -type d \( -path ./.git -o -path ./.svn \) -prune -o -exec svn lock --force {} \;'''

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
    dir_ = os.path.join(os.getcwd(), DIRECTORY_MAP[repo_name][0])

    os.chdir(dir_)
    shia = ""
    try:
        shia = do_command('git rev-parse HEAD', return_=True)
    except subprocess.CalledProcessError as error:
        print('Error.')
        print(error.output.decode('utf-8'))
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
        print('This is the first run, please be patient as cloning and setting up might take time.')
        do_command('svn co "'+svn_url+'" "'+name+'"')
        print('Cloned from SVN successfully.')
        os.chdir(dir_)

        print('Setting ignores for svn')
        do_command('svn propset svn:ignore .git .')
    except subprocess.CalledProcessError as error:
        print('Error!')
        print(error.output.decode('utf-8'))

    os.chdir(dir_)
    try:
        print('Now trying to gain lock access. May fail.')
        do_command(UNLOCK_COMMAND)
        print('Unlocking might have worked.')
    except subprocess.CalledProcessError as error:
        print('Unlocking/locking failed. Please see README#Troubleshooting')
        print(error.output.decode('utf-8'))

    try:
        print('Initializing local repo and setting remotes to GitHub')
        do_command('git init')
        do_command('git remote add origin '+git_url)

        print('Now pulling everything. May take time.')
        try:
            do_command('git pull origin master -f')
        except Exception:
            pass
        do_command('git reset --hard origin/master')
        do_command('svn add --force .')
        try:
            do_command('''svn st | grep ^! | awk '{print " --force "$2}' | xargs svn rm''')
        except Exception:
            pass
    except subprocess.CalledProcessError as error:
        print('Error!')
        print(error.output.decode('utf-8'))
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
        if BREAK_LOCKS_EVERYTIME:
            print('Breaking all locks as stated in config')
            do_command(UNLOCK_COMMAND)
        do_command('svn commit -m "'+commit_message+'"')
        if RELOCK_EVERYTIME:
            print('Now relocking repository.')
            do_command(LOCK_COMMAND)
    except subprocess.CalledProcessError as error:
        print('Error!')
        print(error.output.decode('utf-8'))

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
        try:
            do_command('git pull origin master -f')
        except Exception:
            pass
        do_command('git reset --hard origin/master')
        do_command('svn add --force .')
        try:
            do_command('''svn st | grep ^! | awk '{print " --force "$2}' | xargs svn rm''')
        except Exception:
            pass
    except subprocess.CalledProcessError as error:
        print('Error.')
        print(error.output.decode('utf-8'))
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
    if len(sys.argv)>=2:
        cmd = sys.argv[1]

        if cmd.lower()=='clean':
            print('Do you want to delete all local repository copies? Y/n')
            confirm = input()
            if not confirm or confirm[:1].lower()=='y':
                for (repo_name, value) in DIRECTORY_MAP.items():
                    print('Deleting ', repo_name)
                    dir_ = os.path.join(os.getcwd(),
                        DIRECTORY_MAP[repo_name][0])
                    do_command('rm -rf '+dir_)
                print('Done, exiting.')
                sys.exit(0)


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
