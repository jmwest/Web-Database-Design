from flask import *
from extensions import mysql
from globals import *
from encryptPassword import *

login = Blueprint('login', __name__, template_folder='templates')

#returns a tuple with 4 values: representing (BOOL valid username, STRING algorithm,
#											STRING salt, STRING hash)
def getUserList(givenUsername):
	cur = mysql.connection.cursor()
	checkUsernameStatement = "SELECT * FROM User WHERE username = %(username)s"
	cur.execute(checkUsernameStatement, {'username': givenUsername})
	if (cur.rowcount == 1):
		wholeRow = cur.fetchall()
		#print "found a match"
		listOfAlgSaltHash = wholeRow[0][3].split("$") 
		#print listOfAlgSaltHash 
		return [True, listOfAlgSaltHash[0], listOfAlgSaltHash[1], listOfAlgSaltHash[2]]
	else:
		#print "Randy Orton in a place we've nevr seen him before"
		return [False, '', '', '']


def getFullNameOfUser(username):
	cur = mysql.connection.cursor()
	checkUsernameStatement = "SELECT * FROM User WHERE username = %(username)s"
	cur.execute(checkUsernameStatement, {'username': username})
	fullQuery = cur.fetchall()[0]
	firstname = fullQuery[1]
	lastname = fullQuery[2]
	return [firstname, lastname]


@login.route(route_prefix + '/login', methods=['GET', 'POST'])
def login_route():
	options = {}

	print "Found breadcrumb in URL:"
	print "  Route: " + str(request.args.get('url'))
	query_string = str(request.query_string)
	first_ampersand = query_string.find('&') + 1
	sans_url = query_string[first_ampersand:]
	print "  Other Query Parameters: " + sans_url

	if check_active_session() != None:
		return redirect(url_for('user.user_edit_route'))

	return render_template("login.html", **options)


@login.route(route_prefix + '/api/v1/login', methods=['GET', 'POST'])
def api_login_route():
	print "calling something IN FLASKKK"
	if request.method == 'POST':
		print "Receiving POST request for /api/vi/login"
		json_obj = request.get_json()
		print "  Received payload: " + json.dumps(json_obj)
		username_in = json_obj.get('username')
		password_in = json_obj.get('password')

		if (username_in == None or password_in == None):
			print "ERROR"
			print "You did not provide the necessary fields"
			response = {
				"errors": [
					{
						"message": "You did not provide the necessary fields"
					}
				]
			}
			return jsonify(**response), 422

		else:
			print "Received login info:"
			print "  Username: " + username_in
			print "  Password: " + password_in

			#if username is in database
			listValidAlgSaltHash = getUserList(username_in)

			if listValidAlgSaltHash[0]:
				#hash the password input they gave
				givenPassword = password_in
				hashOfWhatTheyInput = encryptPassword(listValidAlgSaltHash[1], givenPassword, listValidAlgSaltHash[2])[1]
				if hashOfWhatTheyInput == listValidAlgSaltHash[3]:
					session['username'] = username_in
					fullName = getFullNameOfUser(session['username'])
					session['firstname'] = fullName[0]
					session['lastname'] = fullName[1]
					print "Logged in successfully as: " + username_in
					response = {
						"username": username_in
					}
					print "Response payload:"
					print json.dumps(response)
					return jsonify(**response), 200
				else:
					print "ERROR"
					print "Password is incorrect for the specified username"
					response = {
						"errors": [
							{
								"message": "Password is incorrect for the specified username"
							}
						]
					}
					return jsonify(**response), 422
			else:
				print "ERROR"
				print "Username does not exist"
				response = {
					"errors": [
						{
							"message": "Username does not exist"
						}
					]
				}
				return jsonify(**response), 404


