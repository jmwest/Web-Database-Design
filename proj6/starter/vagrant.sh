#!/usr/bin/env bash

# Upgrade apt-get first
sudo apt-get update

# Install the only editors you'll ever need
sudo apt-get install vim emacs --yes

# Getting Java so that we can run hadoop
# So we can add-apt-repository
sudo apt-get install python-software-properties software-properties-common --yes

sudo add-apt-repository ppa:ubuntu-toolchain-r/test --yes
sudo apt-get update
sudo apt-get install g++-4.8 --yes
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-4.8 50

sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update

# These two lines are stolen from: http://askubuntu.com/questions/190582/installing-java-automatically-with-silent-option
# This is to get rid of the license prompt that oracle always gives you
echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections
echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections
# Intsall oracle java because open-jdk causes issues
sudo apt-get install oracle-java7-installer --yes
export JAVA_HOME=/usr/lib/jvm/java-7-oracle

cd /vagrant
# Get the hadoop tar, and move it into the /vagrant directory
wget http://mirror.nexcess.net/apache/hadoop/common/hadoop-2.7.2/hadoop-2.7.2.tar.gz
tar xvxf hadoop-2.7.2.tar.gz
rm hadoop-2.7.2.tar.gz
mv hadoop-2.7.2 hadoop
cd ./hadoop
export JAVA_HOME=/usr/lib/jvm/java-7-oracle

# Get staff starter code, and make it executable
wget http://www-personal.umich.edu/~irbowen/mapreduce.tar.gz
tar xzvf mapreduce.tar.gz
rm mapreduce.tar.gz	 
chmod +x run.sh

# Install Python pip with --yes as the default argument
sudo apt-get install python-pip --yes

# Install virtualenv used for 485 projects
sudo pip install virtualenv

# By default, while installing MySQL, there will be a blocking prompt asking you to enter the password
# Next two lines set the default password of root so there is no prompt during installation
sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password password root'
sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password root'

# Install MySQL server with the default argument --yes
sudo apt-get install mysql-server --yes
sudo apt-get install build-essential python-dev libmysqlclient-dev --yes
# So that we can load xml infile
sudo printf "\n[mysqld]\nlocal-infile\n\n[mysql]\nlocal-infile\n" >> /etc/mysql/my.cnf

# Go to working directory
# This folder is synced on the VM with your local directory where the Vagrantfile is
cd /vagrant
rm -rf venv

# Set up a virtual environment in the current working directory
virtualenv venv --distribute --always-copy

# Use the virtual environment as the terminal shell
source venv/bin/activate

# Install the project requirements given in the requirements.txt file in your working directory
pip install -r requirements.txt
