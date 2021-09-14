from controllers.encryptPassword import *

algorithm = "sha512"
passwords = [ "paulpass93", "rebeccapass15", "bob1pass" ]

for p in passwords:
	print "    Password: " + p
	print "For Database: " + str(createPasswordForDatabaseInsert(algorithm, p))
	print ''