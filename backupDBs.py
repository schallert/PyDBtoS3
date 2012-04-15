try:
	import simplejson as json
except ImportError:
	import json
import subprocess, tarfile, os, ConfigParser
from subprocess import Popen
from datetime import datetime
from pytz import timezone
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.s3.bucket import Bucket

# Load config from json file
config = json.load(open('config.json'))

# Setup configuration vars
server_name = config['mysql']['SERVER_NAME']
databases = [db for db in config['mysql']['databases']]
MYSQL_DUMP_PATH = config['mysql']['MYSQL_DUMP_PATH']
DB_USER = config['mysql']['DB_USER']
DB_PASS = config['mysql']['DB_PASS']

# String to be used in mysqldump call
user_string = '-u ' + DB_USER + ' -p' + DB_PASS

# TODO: prefix the tar file with a shortname of the local server
def tarFileHelper():
	# Loop over databases to be backed up
	for db in databases:
		# Current time, format as you like
		cur_time = datetime.now(timezone('US/Eastern')).strftime('%m-%d-%Y_%H.%M.%S')
		# Name of the tar file for the archive
		tarName = db + '_' + cur_time + '.tar.gz'

		# Calls to mysqldump
		# I choose to dump my table structure and actual table data files separately
		schemaproc = Popen(MYSQL_DUMP_PATH + ' --no-data ' + user_string + ' -x ' + db,
					shell=True, 
					stdout=subprocess.PIPE, 
					stderr=subprocess.STDOUT
			)
		dataproc = Popen(MYSQL_DUMP_PATH + ' --no-create-info ' + user_string + ' -x ' + db,
					shell=True, 
					stdout=subprocess.PIPE, 
					stderr=subprocess.STDOUT
			)
		# Write mysqldump to files. Didn't use tempfiles because those caused issues and
		# are known to have some cross-platform compatability issues
		schematemp = file(db+'_schema.sql', 'w')
		datatemp = file(db+'_data.sql', 'w')
		schematemp.write(schemaproc.communicate()[0])
		datatemp.write(dataproc.communicate()[0])
		schematemp.close()
		datatemp.close()

		# Add dumped schema files to tar archive
		tarFile = tar = tarfile.open( (os.path.join(os.getcwd(), tarName)), "w|gz")
		tarFile.add(schematemp.name, db + '_schema.sql')
		tarFile.add(datatemp.name, db + '_data.sql')
		tarFile.close()
		# Remove the temp dump files
		os.remove(schematemp.name)
		os.remove(datatemp.name)
		yield tarFile.name

key_id = config['aws']['AWS_ACCESS_KEY_ID']
secret_key = config['aws']['AWS_SECRET_ACCESS_KEY']
db_bucket_name = config['aws']['BACKUP_BUCKET']

s3conn = S3Connection(key_id, secret_key)

# Check if there's already a bucket for the desired bucket name
if not db_bucket_name in [b.name for b in s3conn.get_all_buckets()]:
	db_bucket = s3conn.create_bucket(db_bucket_name)
else:
	db_bucket = s3conn.get_bucket(db_bucket_name)

# Loop over created tar files, send them to S3
for backup_tar in tarFileHelper():
	key = Key(db_bucket)
	# Prefix the tar file with the current server name, so it looks
	# like the tar file is in a folder with the name of the server
	key.key = server_name + '/' + os.path.basename(backup_tar)
	key.set_contents_from_filename(backup_tar)
	key.close()
	# Remove tar file after transfer
	os.remove(backup_tar)