from flask import *
from extensions import mysql

main = Blueprint('main', __name__, template_folder='templates')

# Make sure specified URLs from spec have routes here

# /
# Homepage, Browse List of Users
@main.route('/')
def main_route():
    return render_template("index.html")

# /album
# Thumbnail View of an Album
@main.route('/album')
def album_route():
	# Do stuff
	return render_template("album.html")

# /album/edit
# Editing an Album -- Add/Delete Pictures
# TODO


# /albums
# Browsing Albums for a Particular User
@main.route('/albums')
def albums_route():
	return render_template("albums.html")

# /albums/edit
# Editing the List of Albums - Delete/Add Albums
# TODO

# /pic
# View Picture with Prev/Next Links
# TODO

# @main.route('/messages')
# def show_messages():
# 	cur = mysql.connection.cursor()
# 	cur.execute('''SELECT * FROM project1.messages''')    
# 	msgs = cur.fetchall()
# 	output = "<br>".join("Message #{0}: {1}".format(msgs.index(msg), msg[0]) for msg in msgs)
# 	return output