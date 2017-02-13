publicmeetings
==============

A simple Django application for collecting and sharing information about public meetings held by elected officials.

Assumptions
-----------

* Python 3.5+
* PostgreSQL 9.5
* Virtualenvwrapper

Installation
------------

Create a virtual environment:

    mkvirtualenv --python=`which python3` publicmeetings

Activate the virtualenv:

    workon publicmeetings

Install the requirements:

    pip install -r requirements.txt


Create the database:

    createdb publicmeetings


Configuration
-------------

Configuration should go in environment variables.  For local development, put them in an environment file such as `.env`.  Then source it and run the local development server:

    env $(cat ./.env | xargs) ./manage.py runserver

Many of these configuration variables are Django core settings.

### DEBUG

Examples:

    DEBUG=False


### SECRET_KEY

Examples:

    SECRET_KEY=y_%mr87r3&kmp4s&2-h(!t3vl#-4o$nma^71ght1l+4qh_%6nz)

### DATABASE_URL

Examples:

    DATABASE_URL=postgresql://publicmeetings:publicmeetings@localhost/publicmeetings

    # This one works if you have postgres configured to connect through 
    # sockets without a password
    DATABASE_URL=postgresql:///publicmeetings

### GOOGLE_API_KEY

Google API key generated from the [credentials page](https://console.developers.google.com/apis/credentials) in the Google Developers API console.

### EMAIL_HOST

Examples:

    EMAIL_HOST=smtp.sendgrid.net

### EMAIL_HOST_USER

Examples:

    EMAIL_HOST_USER=publicmeetings

### EMAIL_HOST_PASSWORD

Examples:

    EMAIL_HOST_PASSWORD=y0urp455w0rdh3r3

### EMAIL_PORT

Examples:

    EMAIL_PORT=587

### EMAIL_USE_TLS

Examples:

    EMAIL_USE_TLS=True

### ALLOWED_HOSTS

Examples:

    ALLOWED_HOSTS=*

    ALLOWED_HOSTS=yourapp.herokupapp.com


Load info for U.S. Representatives
----------------------------------

    ./manage.py createusreps --infile appalachia_ocd_ids.txt

Build front-end assets
----------------------

Install the build dependencies:

    npm install

To rebuild the assets:

    npm run build
