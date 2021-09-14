CREATE TABLE messages
(
	message VARCHAR(140),
	
	CONSTRAINT pk_messages PRIMARY KEY (message)
);
INSERT INTO messages VALUES ( "Hello World! This is the #1 message." );
INSERT INTO messages VALUES ( "Hello World! This is the #2 message." );