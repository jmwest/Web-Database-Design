from flask import *
from extensions import mysql
from globals import route_prefix

main = Blueprint('main', __name__, template_folder='templates')

# /
# Homepage, Browse List of Users
@main.route(route_prefix + '/')
def main_route():
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM User")    
	list_of_users = cur.fetchall()

	# Match the array in each user to each array and make a new array
	# for the key-value pairing
	attributed_list_of_users = []
	for user in list_of_users:
		attributed_user = {
			"username": user[0],
			"firstname": user[1],
			"lastname": user[2],
			"password": user[3],
			"email": user[4],
		}
		attributed_list_of_users.append(attributed_user)
	options = {
		"users": attributed_list_of_users
	}
	return render_template("index.html", **options)