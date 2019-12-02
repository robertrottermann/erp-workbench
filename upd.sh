#/bin/bash
echo 'workbench'
echo '--------'
(git pull)
echo 'passwords'
echo '---------'
(cd robert_priv; svn up)
(git pull)
echo 'siteslist'
echo '---------'
(cd sites_list/redo2oo; git pull)


