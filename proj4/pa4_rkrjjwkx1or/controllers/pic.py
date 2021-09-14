from flask import *
from extensions import mysql
from globals import *
from album import update_lastupdated

pic = Blueprint('pic', __name__, template_folder='templates')

# /pic
# View Picture with Prev/Next Links
@pic.route(route_prefix + '/pic', methods=['GET', 'POST'])
def pic_route():

	#Get current logged in user
	logged_in_user = check_active_session()
	
	logged_in = True
	if logged_in_user is None:
		logged_in = False

	response = {
		"logged_in": logged_in
	}

	return render_template("pic.html", **response)

@pic.route(route_prefix + '/api/v1/pic/<picid>', methods=['GET', 'POST', 'PUT'])
def api_pic_route(picid):
	cur = mysql.connection.cursor()
	
	albumid_in = None
	caption_in = None
	format_in = None
	next_in = None
	picid_in = None
	prev_in = None
	
	############################################################################
	# PUT and POST
	# Check if all fields are filled.
	# Otherwise, immediately return 422.
	############################################################################
	if request.method == 'PUT'or request.method == 'POST':
		print "Receiving PUT request for /api/vi/pic/<picid>"
		json_obj = request.get_json()
		print "  Received payload: " + json.dumps(json_obj)
		albumid_in = json_obj.get('albumid')
		caption_in = json_obj.get('caption')
		format_in = json_obj.get('format')
		next_in = json_obj.get('next')
		picid_in = json_obj.get('picid')
		prev_in = json_obj.get('prev')

		# if (albumid_in == None or caption_in == None or format_in == None or next_in == None or picid_in == None or prev_in == None):
		if (albumid_in == None or caption_in == None or format_in == None or next_in == None or picid_in == None or prev_in == None):
			print "ERROR", "You did not provide the necessary fields"
			response = {
				"errors": [
					{
						"message": "You did not provide the necessary fields"
					}
				]
			}
			return jsonify(**response), 422
	
	# Get the current picture id
	currentPicId = picid

	############################################################################
	# GET, POST, PUT
	# Check if the picture exists.
	# Otherwise, immediately return 404.
	############################################################################
	checkIDStatement = "SELECT * FROM Photo WHERE picid = %(id)s"
	cur.execute(checkIDStatement, {'id': currentPicId})
	if (cur.rowcount <= 0):
		print "ERROR", "Picture does not exist."
		response = {
			"errors": [
				{
					"message": "The requested resource could not be found"
				}
			]
		}
		return jsonify(**response), 404

	# Get the albumid of this specific picture
	select_stmt = "SELECT albumid, sequencenum FROM Contain WHERE picid = %(picid)s"
	cur.execute(select_stmt, { 'picid': currentPicId })
	
	albumid_sequencenum = cur.fetchall();
	currentAlbumId = albumid_sequencenum[0][0];
	currentSequenceNum = albumid_sequencenum[0][1];

	#determine if pubic or private
	#

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
	
	############################################################################
	# GET, POST, PUT
	# Check if the user has access.
	# If not, immediately return a 401 if they are not logged in.
	# If they are logged in and don't have access, immmediately return a 404.
	############################################################################
	albumAccessStatement = "SELECT access FROM Album WHERE albumid = %(id)s"
	cur.execute(albumAccessStatement, { 'id': currentAlbumId })
	album_access = cur.fetchall()[0][0]
	if album_access == 'private':
		if logged_in_user is None:
			response = {
				"errors": [
					{
						"message": "You do not have the necessary credentials for the resource"
					}
				]
			}
			return jsonify(**response), 401
		
		else:
			user_has_access = False
			if logged_in_user == album_owner:
				user_has_access = True
			for a_user in approved_users:
				if logged_in_user == a_user[0]:
					user_has_access = True
					break
			if user_has_access == False:
				response = {
					"errors": [
						{
							"message": "You do not have the necessary permissions for the resource"
						}
					]
				}
				return jsonify(**response), 403

	############################################################################
	# GET, POST, PUT
	# Check if the user has access.
	# If not, immediately return a 401 if they are not logged in.
	# If they are logged in and don't have access, immmediately return a 404.
	############################################################################

	#####################################

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


	# Return a JSON Object containing the album and pic containing the picture information
	attributed_picture = {
		"picid": picture[0][0],
		"format": picture[0][1],
		"date": picture[0][2],
		"caption": caption[0][0]
	}

	json_next = nextPicInfo['picid']
	json_prev = previousPicInfo['picid']

	response = {
		"albumid": currentAlbumId,
		"caption": caption[0][0],
		"format": picture[0][1],
		"next": "",
		"picid": currentPicId,
		"prev": ""
	}

	if (nextPicInfo['picid'] != 'make america great again'):
		response['next'] = nextPicInfo['picid']
		
	if (previousPicInfo['picid'] != 'make america great again'):
		response['prev'] = previousPicInfo['picid']

	# Post a new caption
	if request.method == 'PUT':
		print caption_in
		if len(caption_in) > 255:
			print "caption > 255"
			response = {
				"errors": [
					{
						"message": "The requested resource could not be found"
					}
				]
			}
			return jsonify(**response), 404

		############################################################################
		# PUT
		# Make sure that only the caption was changed.
		# Otherwise, immediately return 403.
		############################################################################
		# albumid_in = None
		# caption_in = None
		# format_in = None
		# next_in = None
		# picid_in = None
		# prev_in = None
		if (response['albumid'] != albumid_in or response['format'] != format_in or response['next'] != next_in or response['picid'] != picid_in or response['prev'] != prev_in):
			print "ERROR", "Something other than caption was modified in the JSON request."
			response = {
				"errors": [
					{
						"message": "You can only update caption"
					}
				]
			}
			return jsonify(**response), 403
		
		update_caption_stmt = "UPDATE Contain SET caption=%(caption)s WHERE picid=%(picid)s"
		cur.execute(update_caption_stmt, { 'caption': caption_in, 'picid': picid_in })
		mysql.connection.commit()
		update_lastupdated(cur, albumid_in)
		print "caption changed to " + caption_in
		response['caption'] = caption_in

	return jsonify(**response)


	# options = {
	# 	"picture": attributed_picture,
	# 	"albumId": currentAlbumId,
	# 	"previousPicInfo": previousPicInfo,
	# 	"nextPicInfo": nextPicInfo,
	# 	"userIsOwner": logged_in_user == album_owner
	# }

	# return render_template("pic.html", **options)
