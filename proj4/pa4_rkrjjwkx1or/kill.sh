# SERVER SPECIFIC VARIABLES
SERVER=eecs485-22.eecs.umich.edu	# TODO set your server here!
PORT1=3000												# TODO set your ports here!
PORT2=3001

# GROUP VARIABLES
GROUP=group61											# TODO set you group number
SECRET=group61										# TODO set your secret

# STATIC RESOURCE PATH						# TODO make sure you have a backup folder
IMAGES=static/images							# and that the paths are correct
IMAGES_BACKUP=static/images_backup

# SQL SCRIPT PATH									# TODO make sure paths are correct
SQL_CREATE=sql/tbl_create.sql
SQL_LOAD=sql/load_data.sql

# PA4_CPP PATH
PA4_CPP=pa4_CPP/

# ASSIGNMENT VARIABLES
PA=pa1														# TODO project number here (for sql)

# SCRIPT COMMANDS
echo "Searching for gunicorn process on $(whoami)..."
GUNI_PID=$(ps aux | grep $(whoami) | grep '[g]unicorn' | awk '{print $2}')
if [ -z "$GUNI_PID" ]; then
	echo "No gunicorn process found."
else
	kill $GUNI_PID
	echo "Gunicorn process terminated."
fi

echo "Searching for CPP process on $(whoami)..."
CPP_PID=$(ps aux | grep $(whoami) | grep 'indexServer' | awk '{print $2}')
if [ -z "$CPP_PID" ]; then
	echo "No C++ process found."
else
	kill $CPP_PID
	echo "C++ process terminated."
fi
