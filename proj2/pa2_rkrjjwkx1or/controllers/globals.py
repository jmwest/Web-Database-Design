from flask import *

route_prefix = '/rkrjjwkx1or/pa2'

# Returns a username if someone is logged in, but "offline"
def check_active_session():
	if 'username' in session:
		return session['username'];
	return None;