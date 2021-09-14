# EECS 485: Project 1

### Group Name: Raynor's Raiders
Group info:
```
Secret Key: rkrjjwkx1or
Host: eecs485-22.eecs.umich.edu
Username: <your uniqname>
Password: <your umich password>
MySQL Username: group61
MySQL Password: group61
Project 1 Database: group61pa1
Ports: 3000, 3001
```

### Members
  - John West (johnwest) - Protoss
    - implemented `/album`, and `/album/edit`
    - handled file addition & deletion from /static and the database
    - debugging
  - Diego Calvo (calvod) - Zerg
  - Nick Cruz (ncruz) - Zerg
    - implemented `/pic`, `/album`, and `/albums`
    - deployed and submitted project
    - managed Github issues

### Live Access
  - [Live Site At Port 3000](http://eecs485-22.eecs.umich.edu:3001/rkrjjwkx1or/pa1/)
  - [Live Site At Port 3001](http://eecs485-22.eecs.umich.edu:3001/rkrjjwkx1or/pa1/)
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
$ git clone https://github.com/EECS485-Winter2016/pa1_rkrjjwkx1or.git
```
And log in with your Github account.

Navigate to the project folder.
```
$ cd pa1_rkrjjwkx1or/
```

**Copy the images in static/images/ to the remote server.**
In another terminal, navigate to a local copy of your repo. Go to your static/images folder (with the hash images). In order to have the photos on the server, you need to perform an `scp` command that transfers the contents of your local static/images/ folder to a static/images/ folder on ther server. This copies a folder from a **local** directory to a **remote** directory.
When you are in your local static/ folder, type in: (change username to your username)
```
Local:
$ scp -r images uniqname@eecs485-22.eecs.umich.edu:/var/www/html/group61/pa1_rkrjjwkx1or/static/images
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
app.config['MYSQL_DB'] = 'group61pa1'
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

##### Step 2: Checking and killing processes
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

##### Step 3: Deploying
**This assumes there is no process currently running.**
Make sure your path is `/var/www/html/group61/pa1_rkrjjwkx1or` (run `pwd` to get your path).
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


### Extra:
  - zerg4lyfe
