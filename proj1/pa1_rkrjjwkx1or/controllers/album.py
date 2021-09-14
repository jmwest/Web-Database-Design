import os
from flask import *
from werkzeug import secure_filename
from extensions import mysql
from globals import route_prefix
import datetime
import hashlib

album = Blueprint('album', __name__, template_folder='templates')

# Get all of the pictures in the album from the database
def get_pictures(isEdit):
	cur = mysql.connection.cursor()
	
	# Get the current album
	currentAlbumId = request.args.get('id')

	#404 if album id doesn't exist
	checkIDStatement = "SELECT * FROM Album WHERE albumid = %(id)s"
	cur.execute(checkIDStatement, {'id': currentAlbumId})
	if (cur.rowcount <= 0):
		return render_template('404.html'), 404

	username_stmt = "SELECT username FROM Album "
	username_stmt += "WHERE albumid=%(albumid)s"
	
	cur.execute(username_stmt, { 'albumid': currentAlbumId })
	user = cur.fetchall()[0][0]
	
	# Get all pictures of this album with the current id
	select_stmt = "SELECT Contain.sequencenum, Contain.picid, Photo.format "
	select_stmt += "FROM Contain "
	select_stmt += "INNER JOIN Photo "
	select_stmt += "ON Contain.picid = Photo.picid "
	select_stmt += "WHERE Contain.albumid = %(albumid)s"
	select_stmt += "ORDER BY Contain.sequencenum ASC"
	cur.execute(select_stmt, { 'albumid': currentAlbumId })
	
	list_of_pictures = cur.fetchall();
	attributed_list_of_pictures = []
	for picture in list_of_pictures:
		attributed_picture = {
			"sequencenum": picture[0],
			"picid": picture[1],
			"format": picture[2]
		}
		attributed_list_of_pictures.append(attributed_picture)
	
	options = {
		"edit": isEdit,
		"pictures": attributed_list_of_pictures,
		"albumid": currentAlbumId,
		"username": user
	}
	return options

# Check if filename is valid
def valid_filename(filename):
	return '.' in filename and (filename.rsplit('.',1)[1]).lower() in current_app.config['ALLOWED_EXTENSIONS']

# Update Album lastupdated date
def update_lastupdated(cursor, albumid, date):
	update_stmt = "UPDATE Album "
	update_stmt += "SET lastupdated=%(new_date)s "
	update_stmt += "WHERE albumid=%(current_albumid)s"

	cursor.execute(update_stmt, { 'new_date': date, 'current_albumid': albumid})

# Add Picture to the Album
def add_picture(request):
	f = request.files['file']
	if f and valid_filename(f.filename):
		
		# Get necessary info & cursor
		filename = secure_filename(f.filename)
		current_albumid = request.form.get('albumid')
		cursor = mysql.connection.cursor()
		
		# Check albumid
		checkAlbumIDStatement = "SELECT * FROM Album WHERE albumid = %(id)s"
		cursor.execute(checkAlbumIDStatement, {'id': current_albumid})
		if (cursor.rowcount <= 0):
			return render_template('404.html'), 404
		
		# Get title and username for the hash
		get_hash_info = "SELECT title, username "
		get_hash_info += "FROM Album Where albumid = %(albumid)s"
		
		cursor.execute(get_hash_info, { 'albumid': current_albumid})
		result = cursor.fetchall()
		title = result[0][0]
		user_name = result[0][1]
		
		m = hashlib.md5(user_name + title + filename)
		picid = m.hexdigest()
		picFormat = filename.rsplit('.',1)[1]
		# print "JOHN CENAAAA"
		# print picFormat
		
		#404 if pic id already exists
		checkPicIDStatement = "SELECT * FROM Photo WHERE picid = %(id)s"
		cursor.execute(checkPicIDStatement, {'id': picid})
		if (cursor.rowcount > 0):
			return False
		
		# Save the picture to static/images/
		f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], picid + '.' + picFormat))
		
		current_date_and_time = datetime.datetime.today().isoformat()
		current_date = str(current_date_and_time)[:10]
		caption = ''
		
		# Get the number of photos in the album
		num_photos_stmt = "SELECT COUNT(*) FROM Contain "
		num_photos_stmt += "WHERE albumid = %(albumid)s"
		
		cursor.execute(num_photos_stmt, { 'albumid': current_albumid})
		
		sequencenum = 0
		if cursor.fetchall()[0][0] > 0:
			max_sequencenum_stmt = "SELECT MAX(sequencenum) AS sequencenum FROM Contain "
			max_sequencenum_stmt += "WHERE albumid = %(albumid)s"
		
			cursor.execute(max_sequencenum_stmt, { 'albumid': current_albumid})

			max_num = cursor.fetchall()[0][0]
			# print max_num
			sequencenum = int(max_num) + 1
		
		# Insert information into the Photo and Contain dbs
		photo_insert = "INSERT INTO Photo (picid, format, date) VALUES (%s, %s, %s)"
		contain_insert = "INSERT INTO Contain (albumid, picid, caption, sequencenum) VALUES (%s, %s, %s, %s)"
		
		cursor.execute(photo_insert, (picid, picFormat, current_date))
		cursor.execute(contain_insert, (current_albumid, picid, caption, sequencenum))
		update_lastupdated(cursor, current_albumid, current_date)
		
		# Commit changes to db
		mysql.connection.commit()
	
	return True

# Delete pic from the Album
def delete_picture(request):
	cursor = mysql.connection.cursor()
	
	picid = request.form.get('picid')
	current_albumid = request.form.get('albumid')
	
	# Check albumid
	checkAlbumIDStatement = "SELECT * FROM Album WHERE albumid = %(id)s"
	cursor.execute(checkAlbumIDStatement, {'id': current_albumid})
	if (cursor.rowcount <= 0):
		return render_template('404.html'), 404

	# Get sequencenum
	get_sequencenum_stmt = "SELECT sequencenum FROM Contain "
	get_sequencenum_stmt += "WHERE picid=%(picid)s"
	
	cursor.execute(get_sequencenum_stmt, { 'picid': picid })
	
	sequencenum = cursor.fetchall()[0][0]
	
	# Get format and delete from static/image
	format_stmt = "SELECT format FROM Photo "
	format_stmt += "WHERE picid=%(picid)s"
	
	cursor.execute(format_stmt, {'picid': picid})
	if (cursor.rowcount <= 0):
		return render_template('404.html'), 404

	format = cursor.fetchall()[0][0]
	
	os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], picid + '.' + format))
	
	# Delete from Contain and Photo in the db
	contain_stmt = "DELETE FROM Contain "
	contain_stmt += "WHERE picid=%(picid)s"
	photo_stmt = "DELETE FROM Photo "
	photo_stmt += "WHERE picid=%(picid)s"
	
	cursor.execute(contain_stmt, {'picid': picid})
	cursor.execute(photo_stmt, {'picid': picid})
	
	# Get all the pictures in the album to adjust sequencenums
	get_pictures_stmt = "SELECT * FROM Contain "
	get_pictures_stmt += "WHERE albumid=%(albumid)s"
	
	cursor.execute(get_pictures_stmt, { 'albumid': current_albumid })
	album_pictures = cursor.fetchall()
	
	#sequence_stmt = "UPDATE Contain "
	#sequence_stmt += "SET sequencenum=%(sequencenum)s "
	#sequence_stmt += "WHERE picid=%(picid)s"
	
	#for picture in album_pictures:
	#	current_sqnum = picture[3]
	#	if current_sqnum > sequencenum:
	#		cursor.execute(sequence_stmt, {'sequencenum': current_sqnum - 1, 'picid': picture[1]})
	
	current_date_and_time = datetime.datetime.today().isoformat()
	current_date = str(current_date_and_time)[:10]
	update_lastupdated(cursor, current_albumid, current_date)
	
	# Commit changes to db
	mysql.connection.commit()
	
	return

# /album/edit
# Editing an Album -- Add/Delete Pictures
@album.route(route_prefix + '/album/edit', methods=['GET', 'POST'])
def album_edit_route():
	#404 if album id doesn't exist
	cur = mysql.connection.cursor()
	currentAlbumId = request.args.get('id')
	checkIDStatement = "SELECT * FROM Album WHERE albumid = %(id)s"
	cur.execute(checkIDStatement, {'id': currentAlbumId})
	if (cur.rowcount <= 0):
		return render_template('404.html'), 404

	if request.form.get('op') == 'add':
		add_picture_success = add_picture(request)
		if add_picture_success == False:
			return render_template('404.html'), 404
		#return redirect(route_prefix + '/album/edit?id=' + currentAlbumId)
	
	elif request.form.get('op') == 'delete':
		#404 if pic id doesn't exist
		picid = request.form.get('picid')
		checkPicIDStatement = "SELECT * FROM Photo WHERE picid = %(id)s"
		cur.execute(checkPicIDStatement, {'id': picid})
		if (cur.rowcount <= 0):
			return render_template('404.html'), 404
		delete_picture(request)
		return redirect(route_prefix + '/album/edit?id=' + currentAlbumId)

	options = get_pictures(True)
	return render_template("album.html", **options)

# /album
# Thumbnail View of an Album
@album.route(route_prefix + '/album')
def album_route():
	#404 if album id doesn't exist
	cur = mysql.connection.cursor()
	currentAlbumId = request.args.get('id')
	checkIDStatement = "SELECT * FROM Album WHERE albumid = %(id)s"
	cur.execute(checkIDStatement, {'id': currentAlbumId})
	if (cur.rowcount <= 0):
		return render_template('404.html'), 404
	
	options = get_pictures(False)
	return render_template("album.html", **options)
