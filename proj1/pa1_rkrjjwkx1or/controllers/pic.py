from flask import *
from extensions import mysql
from globals import route_prefix

pic = Blueprint('pic', __name__, template_folder='templates')

# /pic
# View Picture with Prev/Next Links
@pic.route(route_prefix + '/pic')
def pic_route():
	cur = mysql.connection.cursor()
	
	# Get the current picture id
	currentPicId = request.args.get('id')

	#404 if bad pic id
	checkIDStatement = "SELECT * FROM Photo WHERE picid = %(id)s"
	cur.execute(checkIDStatement, {'id': currentPicId})
	if (cur.rowcount <= 0):
		return render_template('404.html'), 404

	# Find this specific picture
	select_stmt = "SELECT * FROM Photo WHERE picid = %(picid)s"
	cur.execute(select_stmt, { 'picid': currentPicId })
	
	picture = cur.fetchall();
	attributed_picture = {
		"picid": picture[0][0],
		"format": picture[0][1],
		"date": picture[0][2]
	}

	# Get the albumid of this specific picture
	select_stmt = "SELECT albumid, sequencenum FROM Contain WHERE picid = %(picid)s"
	cur.execute(select_stmt, { 'picid': currentPicId })

	albumid_sequencenum = cur.fetchall();
	currentAlbumId = albumid_sequencenum[0][0];
	currentSequenceNum = albumid_sequencenum[0][1];

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
		"nextPicInfo": nextPicInfo
	}
	return render_template("pic.html", **options)