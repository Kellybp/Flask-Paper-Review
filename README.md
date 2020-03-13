# sam2020
Group 3 MDD 746 project

Steps taken to set up the project:

1. pip3 install virtualenv
2. virtualenv env  (sets up a virtual environment where all th dependencies required for the project is installed)
3. pip install -r requirements.txt

## Execute following command in the root folder
mkdir -p sam2020/static/papers


## Steps to start the project:

1. source env/bin/activate  (Activates the virtual environment. It contains all the dependencies needed for the project to run.)


How to run:python run.py

## Steps to start the database
1) Download PostgreSQL from [here](https://www.postgresql.org/download/) and install the file
2) During installation set password. This will be used for the PostgreSQL superuser *postgres* which will be used at all times when making a connection
3) Sign in at the command line using this (you will be prompted for your password):
    >psql -U postgres
4) Create the database with the command. __Don't forget the semicolon__, it needs to be on *all* database commmands in the psql program:
    >CREATE DATABASE sam2020; 
5) Type the following to quit:
    >\q
6) #### For this part you must be in the same folder as the *db-create.sql* file.
    Run the creation script with the command (This runs the file on the sam2020 database and creates the specified tables): 
      >psql -U postgres -f db-create.sql sam2020
7) Connect to the database using:
    >psql -U postgres sam2020
8) Type this to see all data tables in the database:
    >\dt
__To run sql commands in the psql console they *must* end in a semicolon (;)__
