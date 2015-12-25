# Port to serve on
PORT = 8808
# Whether to take control of locks before every svn commit or not
# this might be expensive in terms of bandwidth, and slow.
# However it prevents others from trying to break locks and make their own
# locks for some reason.
BREAK_LOCKS_EVERYTIME = False

# Repo name -> Directory in which repo exists locally,
#              URL to fetch from GitHub,
#              URL to push to svn
# WARNING: REPO NAME (I.E KEY) MUST == REPO NAME ON GITHUB. ONLY THEN
# WILL git-svn-sync KNOW WHICH REPO TO MESS WITH.
DIRECTORY_MAP = {
    'FakeRepoLulz': ('FakeRepoLulz',
        'git@github.com:svineet/FakeRepoLulz.git',
        'https://svineetorg.svn.cloudforge.com/fakerepolulz5'),
}


# Commit name on github, new sha[:6], Committer name and Committer email 
COMMIT_MESSAGE = "git-svn-sync: {} ({}) - {}<{}>"
INITIAL_COMMIT_MESSAGE = 'git-svn-sync: Sync repository'
# Repo name, sha-old, sha-new
UPDATE_COMMIT_MESSAGE = 'git-svn-sync: {} updated from {} -> {}'
