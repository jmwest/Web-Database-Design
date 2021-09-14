from flask import *

album = Blueprint('album', __name__, template_folder='templates')

@album.route('/album/edit')
def album_edit_route():
	options = {
		"edit": True
	}
	return render_template("album.html", **options)

@album.route('/album')
def album_route():
	options = {
		"edit": False
	}
	return render_template("album.html", **options)
