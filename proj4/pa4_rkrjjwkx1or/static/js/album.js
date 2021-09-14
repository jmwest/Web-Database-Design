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

function fetch_album(albumid)
{
	document.getElementById("content").innerHTML = "";
	console.log("Album.html is loaded ");
	console.log(albumid);
	$.ajax({
		url: url_prefix + '/api/v1/album/' + albumid,
		contentType: "application/json",
		mimeType: "application/json",
		type: 'GET',
		success: function(data) {
			var json_response = JSON.parse(JSON.stringify(data));
			console.log(json_response);

			var element = document.getElementById("content");
			var header = document.createElement("h1");
			header.setAttribute("id", "header");
			header.setAttribute("style", "-webkit-margin-before: 0px; -webkit-margin-after: 0px; text-align: center");
			header.innerHTML = json_response.title;
			var owner = document.createElement("h3");
			owner.setAttribute("id", "owner");
			owner.setAttribute("style", "-webkit-margin-before: 0px; text-align: center")
			owner.innerHTML = json_response.username;

			// Get username ajax call
//			$.ajax({
//				url: url_prefix + '/api/v1/user',
//				contentType: "application/json",
//				mimeType: "application/json",
//				type: 'GET',
//				success: function(data) {
//				   var user_response = JSON.parse(JSON.stringify(data));
//
//				   if (user_response.username == json_response.username) {
//				   var edit = document.createElement("p");
//				   edit.setAttribute("id", "edit");
//				   edit.setAttribute("style", "-webkit-margin-before: 0px; text-align: center; color: blue");
//				   var edit_link = document.createElement("a");
//				   edit_link.innerHTML = "edit";
//				   
//				   var current_url = window.location.href;
//				   var insert = current_url.indexOf('?');
//				   var new_url = current_url.substr(0, insert) + '/edit' + current_url.substr(insert);
//				   
//				   edit_link.setAttribute("href", new_url);
//				   
//				   edit.appendChild(edit_link);
//				   $(edit).insertAfter(owner);
//				   }
//				},
//				error: function(data) {
//				   var login = document.createElement("a");
//				   login.setAttribute("href", window.location.protocol + '//' + window.location.host + url_prefix + '/login');
//				   login.setAttribute("style", "background-color: white;");
//				   login.innerHTML = "log in";
//				   $(element).prepend(login);
//				}
//			});

			element.appendChild(header);
			element.appendChild(owner);

			var table = document.createElement("table");
			table.style.width = "100%";

			for (var i = 0; i < json_response.pics.length; ++i) {
				var row = document.createElement("tr");
				row.style.width = "100%";
				row.style.textAlign = "center";
				var image = document.createElement("IMG");
				var pic = json_response.pics[i];
				image.setAttribute("src", "/static/images/" + pic.picid + "." + pic.format);
				image.setAttribute("id", "pic_" + pic.picid + "_link");
				image.setAttribute("data", pic.picid);

				image.onclick = function () {
					load_picture(this.getAttribute("data"), json_response.username, false);
				};

				image.setAttribute("height", 150);
				var date = document.createElement("p");
				date.className = "date-info";
				date.innerHTML = "Uploaded: " + pic.date;
				var caption = document.createElement("p");
				caption.className = "caption-info";
				caption.innerHTML = "Caption: " + pic.caption;
				row.appendChild(image);
				row.appendChild(date);
				row.appendChild(caption);
				table.appendChild(row);
			}
			element.appendChild(table);
			history.replaceState({route: "album", id: albumid}, "", url_prefix + '/album?id=' + albumid);
		},
		error: function(data) {
		   populate_error(data);
		}
	});
};

function load_picture(picid, owner, reload)
{
	// document.getElementById("header").innerHTML = "PIC";
	document.getElementById("content").innerHTML = "";
	document.getElementById("content").style.textAlign = "center";
	console.log("Pic.html is loaded ");
	//console.log(picid);
	$.ajax({
		   url: url_prefix + '/api/v1/pic/' + picid,
		   contentType: "application/json",
		   mimeType: "application/json",
		   type: 'GET',
		   success: function(data) {
			   var json_response_string = JSON.stringify(data);
			   var json_response = JSON.parse(json_response_string);
			   var element = document.getElementById("content");
			   var table = document.createElement("table");
			   table.setAttribute("align", "center");
			   var row = document.createElement("tr");
			   table.style.textAlign = "center";
			  // row.className = "pic-links";
			   var prev_image = document.createElement("h4");
		   //prev_image.innerHTML = "Previous Image";
		   
		   //prev_image.className = "prev-pic";
			   prev_image.setAttribute("id", "prev_pic");
			   var next_image = document.createElement("h4");
		   //next_image.innerHTML = "Next Image";
		   //next_image.className = "next-pic";
			   next_image.setAttribute("id", "next_pic");
			   var image = document.createElement("IMG");
		   
			   if (json_response.prev != "") {
				   prev_image.onclick = function () { load_picture(json_response.prev, owner, false); };
				   prev_image.innerHTML = "Previous Image";
			   }

			   if (json_response.next != "") {
				   next_image.onclick = function () { load_picture(json_response.next, owner, false); };
				   next_image.innerHTML = "Next Image";
			   }
		   
			   var prev_cell = document.createElement("td");
			   prev_cell.setAttribute("width", 240);
			   prev_cell.appendChild(prev_image);
			   row.appendChild(prev_cell);
			   
			   var next_cell = document.createElement("td");
			   next_cell.setAttribute("width", 240);
			   next_cell.appendChild(next_image);
			   row.appendChild(next_cell);
		   
			   table.appendChild(row);
			   element.appendChild(table);

			   image.setAttribute("src", "/static/images/" + json_response.picid + "." + json_response.format);
			   image.setAttribute("style", "dispay: block; clear: both");
			   element.appendChild(image);

				// Get username ajax call
				$.ajax({
					url: url_prefix + '/api/v1/user',
					contentType: "application/json",
					mimeType: "application/json",
					type: 'GET',
					success: function(data) {
						var user_response = JSON.parse(JSON.stringify(data));

						if (user_response.username == owner) {
							var caption_input = document.createElement("input");
							caption_input.setAttribute("id", "pic_caption_input");
							caption_input.setAttribute("name", "pic_caption_input");
							caption_input.setAttribute("type", "text");
							caption_input.setAttribute("value", json_response.caption);
							caption_input.onkeydown = function(event) {
															key_press(event);
														};
							caption_input.setAttribute("data", json_response_string);
							caption_input.setAttribute("style", "width: 99%");

							element.appendChild(document.createElement("br"));
							element.appendChild(caption_input);
						}
					},
					error: function(data) {
						var caption = document.createElement("p");
						caption.setAttribute("id", "pic_" + picid + "_caption");
						caption.innerHTML = json_response.caption;
						element.appendChild(caption);
					}
				});

			   if (!reload) {
				   window.onpopstate = function (event) {
					   console.log(event.state['route'] + ", " + event.state['id']);
					   if (event.state['route'] == "album") {
						   fetch_album(event.state['id']);
					   }
					   else if (event.state['route'] == "pic") {
						   load_picture(event.state['id'], owner, true);
					   }
				   }
				   var url = url_prefix + '/pic?id=' + picid;
				   history.pushState({route: "pic", id: picid}, "", url);
			   }
		   },
		   error: function(data) {
				populate_error(data);
		   }
	});
};

function key_press(event) {
	if (event.which == 13) {
		var text_box = document.getElementById("pic_caption_input");
		update_caption(text_box.getAttribute("data"), $("#pic_caption_input").val());
	}
};

function update_caption(picture, new_caption) {
	var picture_json = JSON.parse(picture);
	picture_json['caption'] = new_caption;
	
	$.ajax({
		   url: url_prefix + '/api/v1/pic/' + picture_json['picid'],
		   data: JSON.stringify(picture_json),
		   dataType: "json",
		   contentType: "application/json",
		   mimeType: "application/json",
		   type: 'PUT',
		   
		   success: function(data) {
			   console.log("success");
		   },
		   error: function(data) {
			   populate_error(data);
		   }
	});
}

function populate_error(data) {
	var json_response = JSON.parse(data.responseText);
	
	var element = document.getElementById("content");
	var error_p = document.createElement("p");
	error_p.className = "error";
	error_p.innerHTML = json_response.errors[0].message;
	element.appendChild(error_p);
}

// fetch_album(parseInt(window.location.href.slice(window.location.href.indexOf('album?id=') + 'album?id='.length));
