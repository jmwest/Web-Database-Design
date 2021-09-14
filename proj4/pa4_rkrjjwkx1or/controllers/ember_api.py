from datetime import datetime
from collections import namedtuple
from globals import *
from flask import *

#from database import db, get_pic_neighbors
from extensions import mysql


ember_api = Blueprint('ember_api', __name__, template_folder='templates')

Pic = namedtuple('Pic', ['picid', 'format', 'date'])
Contain = namedtuple('Contain', ['albumid', 'picid', 'caption', 'sequencenum'])


def get_pic_neighbors(picid):
	cur = mysql.connection.cursor()
	# Get the albumid of this specific picture
	select_stmt1 = "SELECT albumid, sequencenum FROM Contain WHERE picid = %(picid)s"
	cur.execute(select_stmt1, { 'picid': picid })
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
			nextID = prev_and_next[0][1]
			prevID = ""
		else:
			# Else, only a "previous row" showed up
			prevID = prev_and_next[0][1]
			nextID = ""

	# The query pulled both a previous and next picture (neither first nor last picture in album with 3+ pictures)
	elif numOfPrevAndNext == 2:
		prevID = prev_and_next[0][1]
		nextID = prev_and_next[1][1]

	# The query pulled neither (1 picture in album)
	else:
		prevID = ""
		nextID = ""
	return (currentAlbumId, prevID, nextID)

def execute(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    return cur.fetchall()

def update(query):
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    mysql.connection.commit()
    return cursor.lastrowid

def get_pic_by_id(picid):
	query = "SELECT picid, format, date FROM Photo WHERE picid='%s'" % (picid)
	results = execute(query)
	if len(results) > 0:
		print results[0]
		pic = Pic(*results[0])
		return pic
	else:
		raise RecordNotFound(resource_type='Pic', source={"pointer": "data/attributes/picid"})

def update_caption(picid, caption):
	query = "UPDATE Contain SET caption='%s' WHERE picid='%s'" % (caption, picid)
	try:
		update(query)
	except Exception as e:
		print e
		raise UpdateFailed(resource_type='Pic', source={"pointer": "data/attributes/picid",
														"pointer": "data/attributes/caption"})


def get_contain_by_picid(picid):
	query = "SELECT albumid, picid, caption, sequencenum FROM Contain WHERE picid='%s'" % (picid)
	results = execute(query)
	if len(results) > 0:
		contain = Contain(*results[0])
		return contain
	else:
		raise RecordNotFound(resource_type='Contain', source={"pointer": "data/attributes/picid"})


class JSONAPIException(Exception):

	def __init__(self, title, resource_type, message, status_code, source):
		self.status_code = status_code
		self.title = title
		self.resource_type = resource_type
		self.message = message
		self.status_code = status_code
		self.source = source
		super(JSONAPIException, self).__init__(self.to_json())

	def to_json(self):
		error = dict(status=self.status_code, title=self.title, source=self.source, detail=self.message) 
		return error

class RecordNotFound(JSONAPIException):

	def __init__(self, resource_type, source):
		super(RecordNotFound, self).__init__(title="Resource Not Found", resource_type=resource_type, 
			message="Resource not found for %s. Please verify you specified a valid id." % (resource_type),
			status_code=422, source=source)

class InsertFailed(JSONAPIException):

	def __init__(self, resource_type, source):
		super(InsertFailed, self).__init__(resource_type=resource_type, source=source, 
			title="Insert failed",
			message="Could not insert %s. Please verify correctness of your request." % (resource_type),
			status_code=422)

class UpdateFailed(JSONAPIException):

	def __init__(self, resource_type, source):
		super(UpdateFailed, self).__init__(resource_type=resource_type, source=source, 
			title="Update failed",
			message="Could not update %s. Please verify correctness of your request." % (resource_type),
			status_code=422)


class PicJSONAPI(object):

	def __init__(self, pic, contain):
		self.pic = pic
		self.contain = contain

	def attributes(self):
		albumid, prevID, nextID = get_pic_neighbors(self.pic.picid)
		attributes = {
			"picurl": "{}.{}".format(self.pic.picid, self.pic.format),
			"prevpicid": prevID,
			"nextpicid": nextID,
			"caption": self.contain.caption	
		}
		return attributes


	def relationships(self):
		relationships = {}

		if not relationships:
			return None

		return relationships

	def to_json(self):
		data = {
				"type": "pics",
				"id": self.pic.picid,
				"attributes": self.attributes()
			}

		relationships = self.relationships()
		if relationships is not None:
			data["relationships"] = relationships
		return { "data": data }

@ember_api.route(route_prefix + '/jsonapi/v1/pics/<picid>', methods=['GET'])
def pics(picid):
	print "Charmander used Ember!"
	try:
		pic = get_pic_by_id(picid)
		contain = get_contain_by_picid(picid)
	except RecordNotFound as e:
		response = json.jsonify(errors=[e.to_json()])
		response.status_code=404
		return response

	pic = PicJSONAPI(pic, contain)
	data = pic.to_json()
	return json.jsonify(**data)


@ember_api.route(route_prefix + '/jsonapi/v1/pics/<picid>', methods=['PATCH'])
def patch_caption(picid):
	try:
		data = request.get_json(force=True)["data"]
		caption = data["attributes"]["caption"]
		update_caption(picid, caption)
	except JSONAPIException as e:
		response = json.jsonify(errors=[e.to_json()])
		response.status_code = 422

	response = json.jsonify(data=data)
	response.status_code = 201
	return response


