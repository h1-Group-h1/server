###### Server for the application

## Install & run

1. Clone the repo
2. Create a user for mysql. Credentials are in src/database.py.
3. Create 2 tables, ROYAL_AUTOMATION_BACKEND and ROYAL_AUTOMATION_BROKER_AUTH. Grant the user 'ra_admin' all privileges on these.
4. Run:
``` cd src/ 
uvicorn main:app```