from flask import *
from extensions import mysql
from globals import *
from album import update_lastupdated

pic = Blueprint('pic', __name__, template_folder='templates')

# /pic
# View Picture with Prev/Next Links
@pic.route(route_prefix + '/pic', methods=['GET', 'POST'])
def pic_route():
	cur = mysql.connection.cursor()
	
	# Get the current picture id
	currentPicId = request.args.get('id')

	# Get the albumid of this specific picture
	select_stmt = "SELECT albumid, sequencenum FROM Contain WHERE picid = %(picid)s"
	cur.execute(select_stmt, { 'picid': currentPicId })
	
	albumid_sequencenum = cur.fetchall();
	currentAlbumId = albumid_sequencenum[0][0];
	currentSequenceNum = albumid_sequencenum[0][1];

	#404 if bad pic id
	checkIDStatement = "SELECT * FROM Photo WHERE picid = %(id)s"
	cur.execute(checkIDStatement, {'id': currentPicId})
	if (cur.rowcount <= 0):
		return render_template('404.html'), 404

	######################################
	#403 if not allowed to see pic
	#Get current logged in user
	logged_in_user = check_active_session()

	#Get album owner
	albumOwnerStatement = "SELECT username FROM Album WHERE albumid = %(id)s"
	cur.execute(albumOwnerStatement, { 'id': currentAlbumId })
	album_owner = cur.fetchall()[0][0]
	
	#Get users with access
	usersWithAccessStatement = "SELECT username FROM AlbumAccess "
	usersWithAccessStatement += "WHERE albumid = %(id)s"
	cur.execute(usersWithAccessStatement, { 'id': currentAlbumId })
	approved_users = cur.fetchall()
	
	#Check if album is public or private
	albumAccessStatement = "SELECT access FROM Album WHERE albumid = %(id)s"
	cur.execute(albumAccessStatement, { 'id': currentAlbumId })
	album_access = cur.fetchall()[0][0]
	if album_access == 'private':
		if logged_in_user is None:
			return redirect(route_prefix + '/login')
		
		else:
			user_has_access = False
			if logged_in_user == album_owner:
				user_has_access = True
			for a_user in approved_users:
				if logged_in_user == a_user[0]:
					user_has_access = True
					break
			if user_has_access == False:
				return render_template('403.html'), 403
	#####################################

	# Post a new caption
	if request.form.get('op') == 'caption':
		if len(request.form.get('caption')) > 255:
			return render_template('404.html'), 404
		
		update_caption_stmt = "UPDATE Contain SET caption=%(caption)s WHERE picid=%(picid)s"
		cur.execute(update_caption_stmt, { 'caption': request.form.get('caption'), 'picid': request.form.get('picid') })
		mysql.connection.commit()
		update_lastupdated(cur, currentAlbumId)

	# Find this specific picture
	select_stmt = "SELECT * FROM Photo WHERE picid = %(picid)s"
	cur.execute(select_stmt, { 'picid': currentPicId })
	
	picture = cur.fetchall();

	caption_stmt = "SELECT caption FROM Contain WHERE picid = %(picid)s"
	cur.execute(caption_stmt, { 'picid': currentPicId })

	caption = cur.fetchall();
	attributed_picture = {
		"picid": picture[0][0],
		"format": picture[0][1],
		"date": picture[0][2],
		"caption": caption[0][0]
	}

	# Get the photos that are before and after this one (in sequencenum order)
	select_stmt = "SELECT Contain.sequencenum, Contain.picid, Photo.format "
	select_stmt += "FROM Contain INNER JOIN Photo "
	select_stmt += "ON Contain.picid = Photo.picid "
	select_stmt += "WHERE (Contain.albumid = %(abi)s AND "
	select_stmt += "(Contain.sequencenum = (%(csn)s - 1) OR Contain.sequencenum = (%(csn)s + 1))) "
	select_stmt += "ORDER BY Contain.sequencenum ASC"
	cur.execute(select_stmt, { 'abi': currentAlbumId, 'csn': currentSequenceNum })
	prev_and_next = cur.fetchall();
	numOfPrevAndNext = len(prev_and_next)
	previousPicInfo = {
		"picid": 'make america great again',
		"format": 'make america great again',
	}
	nextPicInfo = {
		"picid": 'make america great again',
		"format": 'make america great again',
	}
	
	# If numOfPrevAndNext == 1, then there is either only one num (first or last picture in album)
	if numOfPrevAndNext == 1:
		if currentSequenceNum == 0:
			# If currentSequenceNum == 1, then only a "next row" showed up
			nextPicInfo['picid'] = prev_and_next[0][1]
			nextPicInfo['format'] = prev_and_next[0][2]
		else:
			# Else, only a "previous row" showed up
			previousPicInfo['picid'] = prev_and_next[0][1]
			previousPicInfo['format'] = prev_and_next[0][2]

	# The query pulled both a previous and next picture (neither first nor last picture in album with 3+ pictures)
	elif numOfPrevAndNext == 2:
		previousPicInfo['picid'] = prev_and_next[0][1]
		previousPicInfo['format'] = prev_and_next[0][2]
		nextPicInfo['picid'] = prev_and_next[1][1]
		nextPicInfo['format'] = prev_and_next[1][2]

	# The query pulled neither (1 picture in album)
		# Don't have to do anything in this case


	options = {
		"picture": attributed_picture,
		"albumId": currentAlbumId,
		"previousPicInfo": previousPicInfo,
		"nextPicInfo": nextPicInfo,
		"userIsOwner": logged_in_user == album_owner
	}

	return render_template("pic.html", **options)
