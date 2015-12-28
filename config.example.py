# Port to serve on
PORT = 8808
# Whether to take control of locks before every svn commit or not
# this might be expensive in terms of bandwidth, and slow.
# However it prevents others from trying to break locks and make their own
# locks for some reason.
BREAK_LOCKS_EVERYTIME = False
# Time saving tricks for debug time, set to False to make pushes faster
# and let others commit to svn repo
RELOCK_EVERYTIME = True

# Repo name -> Directory in which repo exists locally,
#              URL to fetch from GitHub,
#              URL to push to svn
# WARNING: REPO NAME (I.E KEY) MUST == REPO NAME ON GITHUB. ONLY THEN
# WILL git-svn-sync KNOW WHICH REPO TO MESS WITH.
DIRECTORY_MAP = {
    'apertium-html-tools': ('apertium-html-tools',
        'https://github.com/goavki/apertium-html-tools.git',
        'https://svn.code.sf.net/p/apertium/svn/trunk/apertium-tools/apertium-html-tools/'),
}
# Default settings are for apertium-html-tools


# Commit name on github, new sha[:6], Committer name and Committer email 
COMMIT_MESSAGE = "git-svn-sync: {} ({}) - {}<{}>"
INITIAL_COMMIT_MESSAGE = 'git-svn-sync: Sync repository'
# Repo name, sha-old, sha-new
UPDATE_COMMIT_MESSAGE = 'git-svn-sync: {} updated from {} -> {}'
