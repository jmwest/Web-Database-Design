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