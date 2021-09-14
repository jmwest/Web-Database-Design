import os
from flask import *
from extensions import mysql
from globals import *
import datetime

albums = Blueprint('albums', __name__, template_folder='templates')

#404s if username doesn't exist
def check_username(username):
	cur = mysql.connection.cursor()
	checkUsernameStatement = "SELECT * FROM User WHERE username = %(username)s"
	cur.execute(checkUsernameStatement, {'username': username})
	if (cur.rowcount <= 0):
		return render_template('404.html'), 404

#returns an attributed list of all albums for a user
#can choose between all albums or just the public
def attributedListOfAlbumsOwned(username, publicOrAll):
	cur = mysql.connection.cursor()
	if publicOrAll == "all":
		select_stmt = "SELECT * FROM Album WHERE username = %(username)s"
	elif publicOrAll == "public":
		select_stmt = "SELECT * FROM Album WHERE username = %(username)s AND access = 'public'"
	cur.execute(select_stmt, { 'username': username })
	list_of_albums = cur.fetchall()
	attributed_list_of_albums = []
	for album in list_of_albums:
		attributed_album = {
			"albumid": album[0],
			"title": album[1],
			"created": album[2],
			"lastupdated": album[3],
			"username": album[4],
			"access": album[5]
		}
		attributed_list_of_albums.append(attributed_album)
	return attributed_list_of_albums

# /albums/edit
# Editing the List of Albums - Delete/Add Albums
@albums.route(route_prefix + '/albums/edit', methods=['GET', 'POST'])
def albums_edit_route():

	#if no session, redirect to login page
	session_status = check_active_session()
	if not session_status:
		options = {
			"badUsername": False,
			"badCombo": False
		}
		return render_template("login.html", **options)

	# Get the username from the session
	username = session['username']

	#404 if username doesn't exist
	check_username(username)

	cur = mysql.connection.cursor()

	if request.form.get('op') == 'add':
		coolTitle = request.form['title']
		todayDateAndTime = datetime.datetime.today().isoformat()
		todayDate = str(todayDateAndTime)[:10]
		#publicOrPrivate = request.form.get('privacy')
		publicOrPrivate = "private"
		addStatement = "INSERT INTO Album (title, created, lastupdated, username, access) VALUES (%s,%s,%s,%s,%s)"
		cur.execute(addStatement, (coolTitle, todayDate, todayDate, username, publicOrPrivate))
		mysql.connection.commit()

	elif request.form.get('op') == 'delete':
		albumIDtoBeDeleted = request.form.get('albumid')
		albumIDasAnInt = int(albumIDtoBeDeleted)
		photoStatement = "SELECT picid FROM Contain WHERE albumid = %(ID)s"
		cur.execute(photoStatement, { 'ID': albumIDasAnInt })
		list_of_picids = cur.fetchall()
		
		formatStatement = "SELECT format FROM Photo WHERE picid = %(ID)s"
		deleteFromContainStatement = "DELETE FROM Contain WHERE picid = %(ID)s"
		deleteFromPhotoStatement = "DELETE FROM Photo WHERE picid = %(ID)s"

		for pictureID in list_of_picids:
			cur.execute(formatStatement, { 'ID': pictureID[0] })
			pictureFormat = cur.fetchall()[0][0]
			cur.execute(deleteFromContainStatement, { 'ID': pictureID[0] })
			cur.execute(deleteFromPhotoStatement, { 'ID': pictureID[0] })
			os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], pictureID[0] + '.' + pictureFormat))
		
		deleteFromAlbumStatement = "DELETE from Album WHERE albumid = %(ID)s"
		cur.execute(deleteFromAlbumStatement, { 'ID': albumIDasAnInt })
		mysql.connection.commit()

	attributed_list_of_albums = attributedListOfAlbumsOwned(username, "all")
	options = {
		"edit": True,
		"albums": attributed_list_of_albums,
		"usernameVal": username,
		"op": ''
	}
	if request.args.get('op') == 'add' or request.args.get('op') == 'delete':
		#make this call /albums route
		#return redirect(url_for('albums_route', **options))
		pass
	return render_template("albums.html", **options)

# /albums
# Browsing Albums for a Particular User
@albums.route(route_prefix + '/albums')
def albums_route():
	print "got into albums_route"
	cur = mysql.connection.cursor()

	#if we got here by manually typing in a url:
	urlUsername = request.args.get('username')
	if urlUsername:
		print "got here by manually typing in a url"
		#404 is username doesn't exist
		check_username(urlUsername)
		#get all public albums this person owns
		attributed_list_of_albums = attributedListOfAlbumsOwned(urlUsername, "public")
		username = urlUsername

	#if we got here by logging in and hitting "my albums"
	else:
		#make sure they're logged in. If not, redirect to login page
		session_status = check_active_session()
		if not session_status:
			options = {
					"badUsername": False,
					"badCombo": False
			}
			return render_template('login.html', **options)

		# Get all albums owned by this person
		attributed_list_of_albums = attributedListOfAlbumsOwned(session['username'], "all")
		username = session['username']
	
	options = {
		"edit": False,
		"albums": attributed_list_of_albums,
		"usernameVal": username
	}
	return render_template("albums.html", **options)