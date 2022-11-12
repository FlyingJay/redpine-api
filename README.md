# Quick Launch 

1. Install [Docker Compose](https://docs.docker.com/compose/install/)
2. Add new/existing [SSH Key](https://gitlab.com/profile/keys)
3. Clone this repository (`git clone git@gitlab.com:redpine/api.git`)
4. Open a terminal and move to the cloned repo
5. Create a file `.docker.env` and enter all the environment variables (excluding `DATABASE_URL`) from the following section in the format `VARIABLE=VALUE`, separated by a line break.
6. Run `docker-compose up`

This should download all dependencies and launch you a server at `localhost:8000`. 

You can log in to `localhost:8000/admin` using user `admin` password `pleasechangeme`.

`glhf q(❂‿❂)p`


# Dependencies

## Python

1. Install Python3.6
2. Create a new virtual environment using `python3 -m venv env`
3. (Unix) Activate the virtual environment by running `source env/bin/activate`
3. (Windows) Run the batch file located at `venv\Scripts\activate.bat`


# Installation

1. Clone the repository
2. Install deps using `pip install -r requirements.txt`
3. Set your database URL in the `DATABASE_URL` environment variable.  For example, `export DATABASE_URL=postgres://127.0.0.1:5432/redpine`
```
App is configured for a Postgres server, modify settings.py to revert to default.
```
4. Run `python manage.py migrate` to migrate the schema


# Environment Variables

```
DATABASE_URL={access url for the database}
FACEBOOK_APP_ID={facebook app id}
FACEBOOK_APP_SECRET={facebook app secret}
MAILGUN_DOMAIN={mailgun domain}
MAILGUN_API_KEY={mailgun api key}
REDPINE_API_BASE_URL={redpine's API url (usually http://localhost:8000 for dev)}
REDPINE_WEBAPP_BASE_URL={webapp url (usually http://localhost:3000 for dev)}
STRIPE_SECRET_KEY={stripe secret key}
STRIPE_PUBLISHABLE_KEY={stripe publishable key}
STRIPE_TEST_MODE={1 to run stripe in test mode; 0 for production mode}
GOOGLE_API_KEY={google api key to be used on the server}
GOOGLE_PUBLIC_API_KEY={google api key to be sent to the client}
```

**The `GOOGLE_PUBLIC_API_KEY` is sent in emails.  It cannot be filtered by requesting host, which means it can be abused.  We should keep an eye on this to make sure it doesn't become a problem..**
