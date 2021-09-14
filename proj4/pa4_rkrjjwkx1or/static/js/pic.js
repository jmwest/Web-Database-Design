//<script type="text/javascript">
//
// /api/v1/pic/<picid> JSON response
//
//{
//	"albumid": 1,
//	"caption": "Pelle Pelle",
//	"format": "jpg",
//	"next": "568ab398af3555d9c991c62b0e4d024c",
//	"picid": "63b1f8027b1cdc739ac89b2dd62cb108",
//	"prev": "933b775e7ea1d6575271103b00e7e965"
//}
//
// /api/v1/album/<albumid> JSON response
//
//{
//	"access": "public",
//	"albumid": 1,
//	"created": "2016­01­01",
//	"lastupdated": "2016­02­02",
//	"pics": [
//			 {
//			 "albumid": 1,
//			 "caption": "",
//			 "date": "2016­01­01",
//			 "format": "jpg",
//			 "picid": "5c00dd3598ce621105cb7062a59e7931",
//			 "sequencenum": 0
//			 },
//			],
//	"title": "I love sports",
//	"username": "sportslover"
//}

"use strict";

var url_prefix_no_first_slash = 'b966cc054de14c43b479/pa3';
var url_prefix = '/' + url_prefix_no_first_slash;

function get_pic_info(picid)
{
	$.ajax({
		   url: url_prefix + '/api/v1/pic/' + picid,
		   contentType: "application/json",
		   mimeType: "application/json",
		   type: 'GET',
		   success: function(data) {
			   var json_response_string = JSON.stringify(data);
			   var json_response = JSON.parse(json_response_string);
		   
			   get_album_info(json_response.albumid, picid);
		   },
		   error: function(data) {
			   populate_error(data);
		   }
	});
};

function get_album_info(albumid, picid)
{
	$.ajax({
		   url: url_prefix + '/api/v1/album/' + albumid,
		   contentType: "application/json",
		   mimeType: "application/json",
		   type: 'GET',
		   success: function(data) {
			   var json_response = JSON.parse(JSON.stringify(data));
		   
			   load_picture(picid, json_response.username, false);
		   },
		   error: function(data) {
			   populate_error(data);
		   }
	});
};

var current_url = window.location.href;
var insert = current_url.indexOf('=');
get_pic_info(current_url.substr(insert + 1));

