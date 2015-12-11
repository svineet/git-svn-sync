git-svn-sync
============

git-svn-sync is a Simple HTTP server that can receive GitHub push hooks. It will update repositories automatically reflecting changes locally.

Running
-------
To run git-svn-sync do:

    python3 main.py

Settings will be taken from config.py. Check config.py for more information about settings. By default git-svn-sync runs on port 8808.

Now that we have the server running we need to tunnel it out. Use `ngrok` for this.

    ./ngrok http 8808

Replace 8808 with the port you set.

Now you will see a external URL for the server you have running locally. Open GitHub and add a `push` hook for this URL to the repositories as required. 

Testing repository for convenience: [FakeRepoLulz](https://github.com/svineet/FakeRepoLulz). Has convenience script 'fake-commit.sh' for making fake commits for testing hook. Please fork and add the ngrok URL you got on running `ngrok http 8808` and test it out.

