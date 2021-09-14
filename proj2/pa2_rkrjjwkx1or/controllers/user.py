from flask import *
from extensions import mysql
from globals import *
from encryptPassword import *
import re
from login import *

user = Blueprint('user', __name__, template_folder='templates')

# Returns false if there is not at least 1 letter or digit
def at_least_1_letter_digit(password1, password2):
	passwords = [ password1.lower(), password2.lower() ]
	for password in passwords:
		has_digit = False
		has_letter = False
		for s in password:
			if s in "abcdefghijklmnopqrstuvwxyz":
				has_digit = True
			if s in "1234567890":
				has_letter = True
		if (has_digit == False or has_letter == False):
			return False
	return True

# Returns True if donald_trump contains only letters, digits, or underscores
# Else returns False
def only_letters_digits_underscores(donald_trump):
	lower = donald_trump.lower()
	for s in lower:
		if (s not in "abcdefghijklmnopqrstuvwxyz1234567890_"): # Add a space if this isn't passing autograder
			return False
	return True

# The username must be unique (though case insensitive)
# ERROR: "This username is taken"
def check_username_if_unique(errors_list, username):
	if (getUserList(username)[0]):
		errors_list.append("This username is taken")

# The username must be at least three characters long
# ERROR: "Usernames must be at least 3 characters long"
def check_username_at_least_3_characters(errors_list, username):
	if (len(username) < 3):
		errors_list.append("Usernames must be at least 3 characters long")

# The username can only have letters, digits and underscores
# ERROR: "Usernames may only contain letters, digits, and underscores"
def check_username_letters_digits_underscores(errors_list, username):
	if (only_letters_digits_underscores(username) == False):
		errors_list.append("Usernames may only contain letters, digits, and underscores")

# The password should be at least 8 characters long
# ERROR: "Passwords must be at least 8 characters long"
def check_password_at_least_8_characters(errors_list, password1, password2):
	if (len(password1) < 8 or len(password2) < 8):
		errors_list.append("Passwords must be at least 8 characters long")

# The password must contain at least one digit and at least one letter
# ERROR: "Passwords must contain at least one letter and one number"
def check_password_at_least_1_digit_and_at_least_1_letter(errors_list, password1, password2):
	if (at_least_1_letter_digit(password1, password2) == False):
		errors_list.append("Passwords must contain at least one letter and one number")

# The password can only have letters, digits and underscores
# ERROR: "Passwords may only contain letters, digits, and underscores"
def check_password_letters_digits_underscores(errors_list, password1, password2):
	if (only_letters_digits_underscores(password1) == False or only_letters_digits_underscores(password2) == False):
		errors_list.append("Passwords may only contain letters, digits, and underscores")

# The first and second password inputs must match
# ERROR: "Passwords do not match"
def check_password_matching(errors_list, password1, password2):
	if (password1 != password2):
		errors_list.append("Passwords do not match")

# Email address should be syntactically valid
# ERROR: "Email address must be valid"
def check_email_if_valid(errors_list, email):
	if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
		errors_list.append("Email address must be valid")

# Except for password, all fields (username, firstname, lastname, and email) have a max length of 20
# "<field> must be no longer than 20 characters"
# (If last name was too long, for example, the error would be "Lastname must be no longer than 20 characters")
def check_all_length(errors_list, data):
	if (len(data[0]) > 20):
		errors_list.append("Username must be no longer than 20 characters")

	if (len(data[1]) > 20):
		errors_list.append("Firstname must be no longer than 20 characters")

	if (len(data[2]) > 20):
		errors_list.append("Lastname must be no longer than 20 characters")

	# if (len(data[3]) > 20):
	# 	errors_list.append("Password1 must be no longer than 20 characters")

	# if (len(data[4]) > 20):
	# 	errors_list.append("Password2 must be no longer than 20 characters")

	if (len(data[5]) > 20):
		errors_list.append("Email must be no longer than 20 characters")

def perform_checks(errors_list, data):
	username = data[0]
	password1 = data[3]
	password2 = data[4]
	email = data[5]

	check_username_if_unique(errors_list, username)
	check_username_at_least_3_characters(errors_list, username)
	check_username_letters_digits_underscores(errors_list, username)
	check_password_at_least_8_characters(errors_list, password1, password2)
	check_password_at_least_1_digit_and_at_least_1_letter(errors_list, password1, password2)
	check_password_letters_digits_underscores(errors_list, password1, password2)
	check_password_matching(errors_list, password1, password2)
	check_email_if_valid(errors_list, email)
	check_all_length(errors_list, data)

@user.route(route_prefix + '/user', methods=['GET', 'POST'])
def user_route():
	options = {
		"edit": False,
		"errors": [],
		"success": "bernie"
	}

	logged_in_user = check_active_session()
	if logged_in_user is not None:
		return redirect(route_prefix + '/user/edit')

	if request.method == 'POST':
		username = request.form.get('username')
		firstname = request.form.get('firstname')
		lastname = request.form.get('lastname')
		password1 = request.form.get('password1')
		password2 = request.form.get('password2')
		email = request.form.get('email')
		data = [ username, firstname, lastname, password1, password2, email ]
		perform_checks(options['errors'], data)

		# If no errors, add a success flag and insert this user into the database
		if (len(options['errors']) == 0):

			# Create password suitable for insertion
			password_hash = createPasswordForDatabaseInsert('sha512', password1)
			print password_hash
			options['success'] = password_hash

			cur = mysql.connection.cursor()
			addStatement = "INSERT INTO User (username, firstname, lastname, password, email) VALUES (%s,%s,%s,%s,%s)"
			cur.execute(addStatement, (username, firstname, lastname, password_hash, email))
			mysql.connection.commit()
			
			return redirect(route_prefix + '/login')

	return render_template("user.html", **options)


def update_firstname(errors_list, new_firstname):
	print "new_firstname: " + new_firstname

	# Validation check
	if (len(new_firstname) > 20):
		errors_list.append("Firstname must be no longer than 20 characters")
	else:
		update_stmt = "UPDATE User "
		update_stmt += "SET firstname=%(firstname)s "
		update_stmt += "WHERE username=%(current_user)s"
		
		cursor = mysql.connection.cursor()
		cursor.execute(update_stmt, { 'firstname': new_firstname, 'current_user': session['username']})
		mysql.connection.commit()

		return "New firstname: " + new_firstname


def update_lastname(errors_list, new_lastname):
	print "new_lastname: " + new_lastname

	# Validation check
	if (len(new_lastname) > 20):
		errors_list.append("Lastname must be no longer than 20 characters")
	else:
		update_stmt = "UPDATE User "
		update_stmt += "SET lastname=%(lastname)s "
		update_stmt += "WHERE username=%(current_user)s"
		
		cursor = mysql.connection.cursor()
		cursor.execute(update_stmt, { 'lastname': new_lastname, 'current_user': session['username']})
		mysql.connection.commit()

		return "New lastname: " + new_lastname

def update_email(errors_list, new_email):
	print "new_email: " + new_email

	# Validation check
	check_email_if_valid(errors_list, new_email)

	# Update if there are no errors
	if (len(errors_list) == 0):
		update_stmt = "UPDATE User "
		update_stmt += "SET email=%(email)s "
		update_stmt += "WHERE username=%(current_user)s"
		
		cursor = mysql.connection.cursor()
		cursor.execute(update_stmt, { 'email': new_email, 'current_user': session['username']})
		mysql.connection.commit()

		return "New email: " + new_email


def update_passwords(errors_list, new_password1, new_password2):
	print "new_password1: " + new_password1
	print "new_password2: " + new_password2

	# Validation check
	check_password_at_least_8_characters(errors_list, new_password1, new_password2)
	check_password_at_least_1_digit_and_at_least_1_letter(errors_list, new_password1, new_password2)
	check_password_letters_digits_underscores(errors_list, new_password1, new_password2)
	check_password_matching(errors_list, new_password1, new_password2)

	# Update if there are no errors
	if (len(errors_list) == 0):

		update_stmt = "UPDATE User "
		update_stmt += "SET password=%(new_password)s "
		update_stmt += "WHERE username=%(current_user)s"

		password_hash = createPasswordForDatabaseInsert('sha512', new_password1)
		print password_hash
		
		cursor = mysql.connection.cursor()
		cursor.execute(update_stmt, { 'new_password': password_hash, 'current_user': session['username']})
		mysql.connection.commit()

		return "New password: " + password_hash
	else:
		return "bernie"

@user.route(route_prefix + '/user/edit', methods=['GET', 'POST'])
def user_edit_route():
	options = {
		"edit": True,
		"errors": [],
		"success": "bernie"
	}

	# Check if there is a logged in user first
	logged_in_user = check_active_session()
	if logged_in_user is None:
		return redirect(route_prefix + '/login')

	if request.method == 'POST':
		request_data = request.form

		# Print some results so you know what's happening
		# print "Receving POST request form data..."
		# for key in request_data.keys():
		#     for value in request_data.getlist(key):
		#         print key,":",value
		# print ''
		# print ''

		# Update the data based on the first key
		firstkey = request_data.keys()[0]
		print "firstkey: " + str(firstkey)
		if (firstkey == "firstname"):
			options['success'] = update_firstname(options['errors'], request_data.getlist(firstkey)[0])
		elif (firstkey == "lastname"):
			options['success'] = update_lastname(options['errors'], request_data.getlist(firstkey)[0])
		elif (firstkey == "email"):
			options['success'] = update_email(options['errors'], request_data.getlist(firstkey)[0])
		else:
			secondkey = request_data.keys()[1]
			options['success'] = update_passwords(options['errors'], request_data.getlist(firstkey)[0], request_data.getlist(secondkey)[0])

		# Update session information
		username_stmt = "SELECT firstname, lastname FROM User "
		username_stmt += "WHERE username=%(current_user)s"
		
		cur = mysql.connection.cursor()
		cur.execute(username_stmt, { 'current_user': session['username'] })
		result = cur.fetchall()
		session['firstname'] = result[0][0]
		session['lastname'] = result[0][1]

	return render_template("user.html", **options)