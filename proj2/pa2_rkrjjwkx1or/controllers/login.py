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
		print "found a match"
		listOfAlgSaltHash = wholeRow[0][3].split("$") 
		print listOfAlgSaltHash 
		return [True, listOfAlgSaltHash[0], listOfAlgSaltHash[1], listOfAlgSaltHash[2]]
	else:
		print "Randy Orton in a place we've nevr seen him before"
		return [False, '', '', '']


def getFullNameOfUser(username):
	cur = mysql.connection.cursor()
	checkUsernameStatement = "SELECT * FROM User WHERE username = %(username)s"
	cur.execute(checkUsernameStatement, {'username': username})
	fullQuery = cur.fetchall()[0]
	firstname = fullQuery[1]
	lastname = fullQuery[2]
	print fullQuery
	print firstname
	print lastname
	return [firstname, lastname]


@login.route(route_prefix + '/login', methods=['GET', 'POST'])
def login_route():
	options = {}
	#they hit the submit button
	if request.method == 'POST':
		print "tried to vote for Trump"
		#if username is in database
		listValidAlgSaltHash = getUserList(request.form['username'])
		if listValidAlgSaltHash[0]:
			#hash the password input they gave
			givenPassword = request.form['password']
			hashOfWhatTheyInput = encryptPassword(listValidAlgSaltHash[1], givenPassword, listValidAlgSaltHash[2])[1]
			#if it matches the hash we stored with their username
			#print "hashOfWhatTheyInput is "+hashOfWhatTheyInput
			#print "listValidAlgSaltHash[3] is "+listValidAlgSaltHash[3]
			if hashOfWhatTheyInput == listValidAlgSaltHash[3]:
				session['username'] = request.form['username']
				fullName = getFullNameOfUser(session['username'])
				session['firstname'] = fullName[0]
				session['lastname'] = fullName[1]
				print "logged in successfully as " + request.form['username']
				options = {
					"badUsername": False,
					"badCombo": False
				}
				return redirect(url_for('main.main_route'))
			else:
				options = {
					"badUsername" : False,
					"badCombo": True
				}
		else:
			options = {
				"badUsername" : True,
				"badCombo": False
			}
	print "Failed to log in, Jeb"
	return render_template("login.html", **options)



