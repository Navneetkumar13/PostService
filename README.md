# Post Service

Description:
This service is a part of another microservice UserService which uses the same the SQL Database as the UserService and communicates with the microservice UserService for the operations. It uses Docker for containerisation.

Tech Stack:
1. It is build on Python and the framework used is Django-Rest-FrameWork.
2. For the Database it is using PostgreSQL Database
3. It also contains Dockerfile through which this service can be containerised

Steps to run the django service:
1. Clone the repo using git clone url
2. Create a Virtual Environment using following command: python -m venv env
3. Activate the environment: source env/bin/activate
4. Install all the requirements in the env. Locate the directory where requirement.txt file is located and run command: pip install -r requirements.txt
5. It uses Sql DB PostgreSql so create .env file define the database properties. For reference you can refer the dummy .env file in the code.
6. After creating Postgresql database and defining all the properties you have to make mirations. Goto where manage.py file is located and run command: python manage.py makemigrations
7. After that run: python manage.py migrate
8. Then you are ready to run the django application: python manage.py runserver
