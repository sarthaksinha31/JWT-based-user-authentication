# Application to perform user authentication using JWT token

## Project Overview
The aim of this project is to create a microservice for user authentication using JSON web tokens. The project follows MVC pattern where the business logic is being handled by the controllers under app/ folder which has various handler functions to perform user authentication and CRUD operations. Inside the src/ folder there are utility functions which promotes code reusability since these functions are being used accross different controller modules.

## Tech Stack:
- Flask
- SQLAlchemy
- Marshmallow

## Steps to run the project
1. Create a virtual environment and activate it then, install the dependencies using pip3 install -r requirements.txt
2. Update the .env file.
3. Go the flask shell using the command python3 -m flask shell
4. Inside the flask shell run the following commands
 - from app.models import User
 - from app.models import TokenBlocklist
 - db.create_all()
5. Exit the flask shell using the cmd ctrl+d and finally run the flask application using "python3 -m flask run"


