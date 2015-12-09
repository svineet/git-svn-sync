Artorias
========

Artorias is a Simple HTTP server that can receive GitHub push hooks. It will update repositories automatically reflecting changes locally.

Running
-------
To run Artorias do:

    python3 main.py

Settings will be taken from config.py. Check config.py for more information about settings. By default Artorias runs on port 8808.

Now that we have the server running we need to tunnel it out. Use `ngrok` for this.

    ./ngrok http 8808

Replace 8808 with the port you set.

Now you will see a external URL for the server you have running locally. Open GitHub and add a `push` hook for this URL. 

Testing repository for convenience: [FakeRepoLulz](https://github.com/svineet/FakeRepoLulz). Has convenience script 'fake-commit.sh' for making fake commits for testing hook.


Why the name Artorias?
----------------------

[The Legend of Artorias the Abysswalker](http://darksouls.wikidot.com/knight-artorias)
