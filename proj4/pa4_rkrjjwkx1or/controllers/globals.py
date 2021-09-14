from flask import *

route_prefix = '/b966cc054de14c43b479/pa4'

# Returns a username if someone is logged in, but "offline"
def check_active_session():
	if 'username' in session:
		return session['username'];
	return None;

def redirect_to_login():
	print "Redirecting to /login..."
	backtrack = str(request.url_rule)
	if (len(request.query_string) > 0):
		print "  Found query parameters in backtrack URL:"
		print "  " + request.query_string
		backtrack += '&' + request.query_string
	return redirect(route_prefix + '/login?url=' + backtrack)