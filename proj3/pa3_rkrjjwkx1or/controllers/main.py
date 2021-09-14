from flask import *
from extensions import mysql
from globals import *

main = Blueprint('main', __name__, template_folder='templates')

# /
# Homepage, Browse List of Albums you have access to 
@main.route(route_prefix + '/')
def main_route():
	cur = mysql.connection.cursor()
	#first: get all public albums
	cur.execute("SELECT * FROM Album WHERE access = 'public'")
	tuple_of_public_albums = cur.fetchall()
	list_of_public_albums = list(tuple_of_public_albums)

	#second: get all albums the user has access to
	list_of_private_albums_user_has_access_to = []
	session_status = check_active_session()
	if session_status:
		print "YES session"
		#first, get the ids of those albums
		username = str(session['username'])
		getAlbumsStatement = "SELECT * FROM AlbumAccess WHERE username = %(username)s"
		cur.execute(getAlbumsStatement, {'username': username})
		id_username_pairs = cur.fetchall()
		list_of_ids_user_has_access_to = []
		for pair in id_username_pairs:
			list_of_ids_user_has_access_to.append(pair[0])

		#second, find the matching titles for those ids
		for id in list_of_ids_user_has_access_to:
			idAsInt = int(id)
			getAlbumTitleStatement = "SELECT title FROM Album WHERE albumid = %(please)s"
			cur.execute(getAlbumTitleStatement, {'please': idAsInt})
			gottenTitle = cur.fetchall()
			list_of_private_albums_user_has_access_to.append((id, gottenTitle[0][0]))

	else:
		print "NO session"

	#third: get all PRIVATE albums the user owns
	list_of_albums_they_own = []
	if session_status:
		username = str(session['username'])
		getAlbumsStatement = "SELECT * FROM Album WHERE username = %(username)s AND access = 'private'"
		cur.execute(getAlbumsStatement, {'username': username})
		tuple_of_albums_they_own = cur.fetchall()
		list_of_albums_they_own = list(tuple_of_albums_they_own)

	#fourth: put them together
	list_of_albums = list_of_public_albums + list_of_private_albums_user_has_access_to + list_of_albums_they_own

	# Match the array in each album to each array and make a new array
	# for the key-value pairing
	attributed_list_of_albums = []
	for album in list_of_albums:
		attributed_album = {
			"album_id": album[0],
			"album_title": album[1]
		}
		attributed_list_of_albums.append(attributed_album)

	#get the list of all users as well
	cur.execute("SELECT * FROM User")
	list_of_users = cur.fetchall()
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
		"users": attributed_list_of_users,
		"albums": attributed_list_of_albums,
		"session_status": session_status
	}
	return render_template("index.html", **options)


#Ember????

@main.route(route_prefix +  '/live')
def live_route():
	return send_file('templates/live.html')


