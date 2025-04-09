# friendsandmountains
Event registration website built with django

## Example website
[Friends and Mountains](http://friends-and-mountains.ch/)

## Features
- Display past and future events
- Event with pre-defined data model, matching our event format
- Add multiple photos as a gallery to each event
- (Todo) Event registration form, manage your participants in the django admin panel
- (Todo) Payment integration with stripe

## How to use for your own events
I built this website to make event organization for mountain weekends, birthdays etc easier.  
Feel free to contribute, fork, or contact me to use it for your own event.

---

## Deploy this website (example: pythonanywhere)
A django website is not as easy to deploy as wordpress, for example. What works well for me is with pythonanywhere.com and a mySQL database:

For a complete step-by-step guide, check out the official PythonAnywhere documentation:
[How to deploy a Django web app with PythonAnywhere](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)

Don't forget about these steps:
- Export staticfiles: `python manage.py collectstatic`
- Create database migrations: `python manage.py makemigrations`
- Apply database migrations: `python manage.py migrate`
- Create an `.env` file on your server (see `.env.example` for reference) and add your secrets there
- If using Stripe, make sure to update your API keys in the `.env` file
