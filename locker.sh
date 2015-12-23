if [[ -f $1 ]]; then
    svn lock $1
fi