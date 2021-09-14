# Generate picid for each photo in our folder

import os
import hashlib
import shutil

footballSequenceNum = -1
sportsSequenceNum = -1
spaceSequenceNum = -1
worldSequenceNum = -1

image_dir = './static/images/'

# Loop through each pic
for filename in os.listdir(image_dir):
	album_title = ""
	albumid = 0
	username = ""
	currentAlbumSequenceNum = 0

	# Determine the album, the username, and the sequence within the album
	if (filename[0:9] == "football_"):
		album_title = "I love football"
		albumid = 2
		username = "sportslover"
		currentAlbumSequenceNum = footballSequenceNum = footballSequenceNum + 1
	elif (filename[0:7] == "sports_"):
		album_title = "I love sports"
		albumid = 1
		username = "sportslover"
		currentAlbumSequenceNum = sportsSequenceNum = sportsSequenceNum + 1
	elif (filename[0:6] == "space_"):
		album_title = "Cool Space Shots"
		albumid = 4
		username = "spacejunkie"
		currentAlbumSequenceNum = spaceSequenceNum = spaceSequenceNum + 1
	elif (filename[0:6] == "world_"):
		album_title = "Around The World"
		albumid = 3
		username = "traveler"
		currentAlbumSequenceNum = worldSequenceNum = worldSequenceNum + 1

	# Generate md5 hash of (username + album_title + filename)
	m = hashlib.md5(username + album_title + filename)
	md5hash = m.hexdigest()

	# Determine the extension of the file
	ticker = 0
	for char in filename:
		if char == '.':
			break
		ticker = ticker + 1
	extension = filename[ticker + 1:]

	# Insert sql command into file load_data.sql
	sqlPhotoInsert = "INSERT INTO Photo\nVALUES (\"" + md5hash + "\", \"" + extension + "\", \"2016-01-01\");\n"
	sqlContainInsert = "INSERT INTO Contain\nVALUES (" + str(albumid) + ", \"" + md5hash + "\", \"\", " + str(currentAlbumSequenceNum) + ");\n\n"
	
	with open("picIDs.sql", "a") as myfile:
		myfile.write(sqlPhotoInsert)
		myfile.write(sqlContainInsert)

	dst_file = image_dir + md5hash + '.' + extension
	shutil.copyfile(image_dir + filename, dst_file)

