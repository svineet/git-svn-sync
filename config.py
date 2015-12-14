# Port to serve on
PORT = 8808

# Repo name -> Directory in which repo exists locally,
#              URL to fetch from GitHub,
#              URL to push to svn
DIRECTORY_MAP = {
    'FakeRepoLulz': ('FakeRepoLulz',
        'https://github.com/svineet/FakeRepoLulz',
        'https://svineetorg.svn.cloudforge.com/fakerepolulz3'),
}


# Commit name on github, new sha[:6], Committer name and Committer email 
COMMIT_MESSAGE = "git-svn-sync: {} ({}) - {}<{}>"
INITIAL_COMMIT_MESSAGE = 'git-svn-sync: Sync repository'
# Repo name, sha-old, sha-new
UPDATE_COMMIT_MESSAGE = 'git-svn-sync: {} updated from {} -> {}'
