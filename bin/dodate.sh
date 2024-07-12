# date
date +"%F"
# var=$(date)
# var=`date`
# echo '$var'

## backup dir format ##
backup_dir=$(date +'%m_%d_%Y_%H_%M')
echo "Backup dir for today: /nas04/backups/${backup_dir}"