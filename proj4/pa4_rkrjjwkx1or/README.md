# EECS 485: Project 4

### Group Name: Raynor's Raiders
Group info:
```
Secret Key: b966cc054de14c43b479
Host: eecs485-22.eecs.umich.edu
Username: <your uniqname>
Password: <your umich password>
MySQL Username: root
MySQL Password: root
Project 4 Database: project1
Ports: 3000, 3001
```

### Final Exam
	main problem in consistency models:
	to keep things consisten between users, remember that different messages take different amounts of time to send

### Members
  - John West (johnwest) - Protoss
    - helped plan data structures and debug
    - built relevant doc list based on user query
    - index_server init
  - Diego Calvo (calvod) - Zerg
    - debug
    - created early versions of Indexer
    - created early versions of process-query inside index_server
  - Nick Cruz (ncruz) - Zerg
    - `search.py`, `search.html`
    - planned data structures
    - helped debug stuff
    - deployed and submitted project

### Live Access
  - [Live Site At Port 3000](http://eecs485-22.eecs.umich.edu:3000/b966cc054de14c43b479/pa3/)
  - [Live Site At Port 3001](http://eecs485-22.eecs.umich.edu:3001/b966cc054de14c43b479/pa3/)
  - [Very Important Background Documentation](https://www.fanfiction.net/s/11219219/1/StarCraft-Legacy)

### How to deploy
#### Step 0: SSH and Server Environment Setup
*You can skip this step if it's already set up. But you still need to SSH into the server to do anything.*
SSH into the server. The host is `eecs485-22.eecs.umich.edu`. Type:
```
$ ssh uniqname@eecs485-22.eecs.umich.edu
```
And enter your password.

You need to navigate to the correct folder with the actual public HTML files. Type:
```
$ cd /var/www/html/group61/
```

**Get the actual files.**
If you type `ls` and see a folder, someone has probably already done the rest of Step 0. **Skip to step 1.**
Else, clone the repo:
```
$ git clone https://github.com/EECS485-Winter2016/pa4_rkrjjwkx1or.git
```
And log in with your Github account.

Navigate to the project folder.
```
$ cd pa4_rkrjjwkx1or/
```

**Copy the images in static/images/ to the remote server.**
In another terminal, navigate to a local copy of your repo. Go to your static/images folder (with the hash images). In order to have the photos on the server, you need to perform an `scp` command that transfers the contents of your local static/images/ folder to a static/images/ folder on ther server. This copies a folder from a **local** directory to a **remote** directory.
When you are in your local static/ folder, type in: (change username to your username)
```
Local:
$ scp -r images uniqname@eecs485-22.eecs.umich.edu:/var/www/html/group61/pa4_rkrjjwkx1or/static/images
```
You can close this terminal process and go back to the remote process (the one that is SSH'd into the server).

**Run the project-0 setup.** You might need to install everything in `requirements.txt`. Type:
```
pip install -r requirements.txt
```
Don't worry if they're not installed, if you run the Gunicorn deployment command later, it'll say `-bash: gunicorn: command not found`. In which case, just run the above command to install it. 

If `venv` is not in the repository, type
```
$ virtualenv venv --distribute
```

**Configure MYSQL.** There is no database here, so you need to load the existing data in the database. Login to MYSQL:
```
$ mysql -u group61 -p
```
The password is `group61`.

Select your database. This should already exist.
```
$ use group61pa1;
```

Make sure there are no tables.
```
$ show tables;
```

If there are none, run the SQL files.
```
$ source sql/tbl_create.sql;
$ source sql/load_data.sql;
```

Once those are set up, you can exit MYSQL.
```
$ exit
```

#### Step 1: Configuring `app.py`
`app.py` is configured to local development. You will need to configure it's contents to work with the server's MYSQL.
Open the `app.py` in nano because nanomasterrace:
```
$ nano app.py
```

Change these lines
```
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'project1'
```
to
```
app.config['MYSQL_USER'] = 'group61'
app.config['MYSQL_PASSWORD'] = 'group61'
app.config['MYSQL_DB'] = 'group61pa3'
```

**(optional) step: Testing `python app.py` on the server**
The bottom of `app.py` will say something like this:
```
# Listen on external IPs
# For us, listen to port 3000 so you can just run 'python app.py' to start the server
if __name__ == '__main__':
    # listen on external IPs
    app.run(host='0.0.0.0', port=3000, debug=True)
```
Change the last line to
```
app.run(host='eecs485-22.eecs.umich.edu', port=3000, debug=True)
```
If you want to test the server with `python app.py`.

#### Step 2: Checking and killing processes
Before deploying, check to make sure it's not already deployed (there might be background processes running).
```
$ ps aux | grep johnwest
$ ps aux | grep calvod
$ ps aux | grep ncruz
```
There will probably be a lot of things running already. But if there is nothing that says "eecs485-22" then there is no process running the server. **Skip to Step 3.**
If there are processes running, find the process number(s) (the second column, right next to all the usernames) and kill them:
```
$ kill 80085 42069
```

#### Step 3: Deploying
**This assumes there is no process currently running.**
Make sure your path is `/var/www/html/group61/pa3_b966cc054de14c43b479` (run `pwd` to get your path).
Turn on your virtual environment.
```
$ source venv/bin/activate
```

Run this command to start a Gunicorn background process.
```
$ gunicorn -b eecs485-22.eecs.umich.edu:3000 -b eecs485-22.eecs.umich.edu:3001 -D app:app
```
### Submitting to the Autograder
[Website for submission](https://class1.eecs.umich.edu/)

git archive command (do this while in the root directory)
```
git archive --format=tar.gz HEAD > sql/source.tar.gz
```

### Curl
You can use the curl command to make requests to any url. It works best with a "curl.txt" file in the same directory as where you made the command.
##### GET Request Template:
```
curl URL_TO_SEND_REQUEST_TO
```

##### POST Request Template:
```
curl -X POST -d @PAYLOAD_FILENAME URL_TO_SEND_REQUEST_TO --header "Content-Type:application/json"
```
There are two things to change here:
  - `PAYLOAD_FILENAME`. This is best used as `curl.txt` (currently being .gitignore'd so we can all test our own). Your `curl.txt` should be some JSON object you would like to send to the URL. Example: `{"username": "brazilians", "password": "huehue"}`
  - `WEBSITE_TO_SEND_REQUEST_TO`. The url is the entire URL to send the paylod to. Example: `http://localhost:3000/b966cc054de14c43b479/pa3/api/v1/login`

This is an example POST request to `/api/v1/login`:
```
curl -X POST -d @curl.txt http://localhost:3000/b966cc054de14c43b479/pa3/api/v1/login --header "Content-Type:application/json"
```
where `curl.txt` contains `{"username": "brazilians", "password": "huehue"}`.

### (Pa4) Running IndexServer and setup

*DO NOT TYPE `vagrant ssh`*

Navigate to `/pa4_CPP`:
```
cd pa4_CPP
```

Clean and compile everything first.
```
make clean
make
```

(if the `requests` module cannot be found, type `pip install requests`)

Make the inverted index file and start the server (see Makefile for full command):
```
make run
```

[optional] Make a search query call (locally) to index server with
```
http://localhost:3002/b966cc054de14c43b479/pa4/search?q=<SEARCH QUERY>
```

[optional] For example: to call "steak eggs", search this in the URL:
```
http://localhost:3002/b966cc054de14c43b479/pa4/search?q=steak%20eggs
```
(or just search something on `http://localhost:3000/b966cc054de14c43b479/pa4/search` and hit search)

In a new terminal, go to the root directory, and type
```
python app.py
```

Now navigate to `/search` and search something. You should get results. Or, go to
[http://localhost:3000/b966cc054de14c43b479/pa4/search?query=steak](http://localhost:3000/b966cc054de14c43b479/pa4/search?query=steak)

### Extra:
  - zerg4lyfe
