from flask import *
from extensions import mysql
from globals import *

logout = Blueprint('logout', __name__, template_folder='templates')

@logout.route(route_prefix + '/logout', methods=['GET', 'POST'])
def logout_route():
	# Kill user
	isActive = check_active_session()
	if isActive:
		session.pop('username', None)
		return redirect(url_for('main.main_route'))

	response = {
		"errors": [
				{
					"message": "You do not have the necessary credentials for the resource"
				}
			]
		}
	return jsonify(**response), 401

@logout.route(route_prefix + '/api/v1/logout', methods=['GET', 'POST'])
def api_logout_route():
	if check_active_session() == None:
		response = {
			"errors": [
					{
						"message": "You do not have the necessary credentials for the resource"
					}
				]
			}
		return jsonify(**response), 401
		
	if request.method == 'POST':
		session.pop('username', None)
		return ('', 204)