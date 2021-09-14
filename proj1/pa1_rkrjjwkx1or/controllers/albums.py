import os
from flask import *
from extensions import mysql
from globals import route_prefix
import datetime

albums = Blueprint('albums', __name__, template_folder='templates')

# /albums/edit
# Editing the List of Albums - Delete/Add Albums
@albums.route(route_prefix + '/albums/edit', methods=['GET', 'POST'])
def albums_edit_route():

	cur = mysql.connection.cursor()

	# Get the username from the query field in the url
	clickedUsername = request.args.get('username')

	#404 is username doesn't exist
	checkUsernameStatement = "SELECT * FROM User WHERE username = %(username)s"
	cur.execute(checkUsernameStatement, {'username': clickedUsername})
	if (cur.rowcount <= 0):
		return render_template('404.html'), 404

	if request.form.get('op') == 'add':
		coolTitle = request.form['title']
		todayDateAndTime = datetime.datetime.today().isoformat()
		todayDate = str(todayDateAndTime)[:10]
		addStatement = "INSERT INTO Album (title, created, lastupdated, username) VALUES (%s,%s,%s,%s)"
		cur.execute(addStatement, (coolTitle, todayDate, todayDate, clickedUsername))
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

	select_stmt = "SELECT * FROM Album WHERE username = %(username)s"
	cur.execute(select_stmt, { 'username': clickedUsername })
	list_of_albums = cur.fetchall()
	attributed_list_of_albums = []
	for album in list_of_albums:
		attributed_album = {
			"albumid": album[0],
			"title": album[1],
			"created": album[2],
			"lastupdated": album[3],
			"username": album[4],
		}
		print 
		attributed_list_of_albums.append(attributed_album)
	options = {
		"edit": False,
		"albums": attributed_list_of_albums,
		"usernameVal": clickedUsername,
		"op": ''
	}
	if request.args.get('op') == 'add' or request.args.get('op') == 'delete':
		#make this call /albums route
		#return redirect(url_for('albums_route', **options))
		pass
	return render_template("albumsEdit.html", **options)

# /albums
# Browsing Albums for a Particular User
@albums.route(route_prefix + '/albums')
def albums_route():
	cur = mysql.connection.cursor()

	# Get the username from the query field in the url
	clickedUsername = request.args.get('username')

	#404 is username doesn't exist
	checkUsernameStatement = "SELECT * FROM User WHERE username = %(username)s"
	cur.execute(checkUsernameStatement, {'username': clickedUsername})
	if (cur.rowcount <= 0):
		return render_template('404.html'), 404

	# Get all albums related to this person
	select_stmt = "SELECT * FROM Album WHERE username = %(username)s"
	cur.execute(select_stmt, { 'username': clickedUsername })

	list_of_albums = cur.fetchall()
	attributed_list_of_albums = []
	for album in list_of_albums:
		attributed_album = {
			"albumid": album[0],
			"title": album[1],
			"created": album[2],
			"lastupdated": album[3],
			"username": album[4],
		}
		attributed_list_of_albums.append(attributed_album)

	options = {
		"edit": False,
		"albums": attributed_list_of_albums,
		"usernameVal": clickedUsername
	}
	return render_template("albums.html", **options)