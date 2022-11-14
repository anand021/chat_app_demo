# chat_app_demo
basic chat APP APIs

Steps to run the Application:

1. create a python vertual environment(python 3.x)

2. install the dependencies from the requirement.txt

3. run migrations:
    python manage.py migrate

4. create super user:
    python manage.py createsuperuser
    
5. manually enable the is_admin flag for the created super user from the database.

6. login with the added credentials and use token received in response for other admin actions.

7. please find the postman collection for the API signatures.
