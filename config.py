# Port to serve on
PORT = 8808

# Repo name -> Directory in which repo exists locally,
#              URL to fetch from GitHub,
#              URL to push to svn
DIRECTORY_MAP = {
    'FakeRepoLulz': ('FakeRepoLulz',
        'https://github.com/svineet/FakeRepoLulz',
        'https://svineetorg.svn.cloudforge.com/fakerepolulz'),
}


# Commit name on github, Committer name and Committer email 
COMMIT_MESSAGE = "{} - {}: {}"
INITIAL_COMMIT_MESSAGE = "[ git-svn-sync Update Repository data ]"
