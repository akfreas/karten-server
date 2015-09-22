#Karten Server


This is the server component to the flashcard iOS app Karten, found here: https://github.com/akfreas/karten-iphone.  The server component is responsible for user creation and management, as well as interaction with the CouchDB instance that the iOS app uses to synchronize its flashcard content.  

#Requirements

You can use the [Karten Chef Cookbook](https://github.com/akfreas/Karten-Chef) to get your instance up and running, otherwise you will need to do the following:


###Install pip requirements

Use `pip install -r requirements.pip` found in the root directory of the project to install the required packages.

###Install CouchDB server

Load up CouchDB and ensure that it's accessible to the machine running the Karten Server.  
Create a user on the server that has the ability to add and delete users, as well as change their password. Then, add this following to your `local_settings.py` file:

    COUCHDB_SERVERS = {
            'Karten' : {
                'url_scheme' : 'http',
                'host'       : '0.0.0.0',
                'port'       : '5984'
            }
        }
    
    COUCHDB_CREDENTIALS = {
            'Karten' : {
                'username' : 'CouchDBUserName',
                'password' : 'CouchDBPassword',
                }
            }

###Management 

Set up your favorite config of web app management tools.  I used gunicorn, supervisor, and Nginx to get started.
