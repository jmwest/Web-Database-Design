all:
	# Reset database
	mysql -u group61 -p group61pa1 < reset_database.sql

	# Killing all processes
	pkill -9 -f /group61

	# Start new processes
	gunicorn -b eecs485-22.eecs.umich.edu:3000 -b eecs485-22.eecs.umich.edu:3001 -D app:app

	# Show processes
	ps aux | grep /group61

show:
	ps aux | grep /group61

deploy:
	gunicorn -b eecs485-22.eecs.umich.edu:3000 -b eecs485-22.eecs.umich.edu:3001 -D app:app

kill:
	pkill -9 -f /group61