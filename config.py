# Port to serve on
PORT = 8808

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


# Commit name on github, new sha[:6], Committer name and Committer email 
COMMIT_MESSAGE = "git-svn-sync: {} ({}) - {}<{}>"
INITIAL_COMMIT_MESSAGE = 'git-svn-sync: Sync repository'
# Repo name, sha-old, sha-new
UPDATE_COMMIT_MESSAGE = 'git-svn-sync: {} updated from {} -> {}'
