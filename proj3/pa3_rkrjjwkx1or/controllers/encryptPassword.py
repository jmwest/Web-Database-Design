import hashlib
import uuid

#this function takes in a plaintext string, and returns the ciphertext with salt
def encryptPassword(algorithm, plainPass, givenSalt = None):
	if givenSalt:
		salt = givenSalt
	else:
		salt = uuid.uuid4().hex # salt as a hex string for storage in db	
	m = hashlib.new(algorithm)
	plainPass = plainPass.encode('utf-8')
	salt = salt.encode('utf-8')
	m.update(salt + plainPass)
	password_hash = m.hexdigest()
	return [ salt, password_hash ]

def createPasswordForDatabaseInsert(algorithm, password):
	encryption = encryptPassword(algorithm, password)
	salt = encryption[0]
	password_hash = encryption[1]
	return "$".join([algorithm,salt,password_hash])