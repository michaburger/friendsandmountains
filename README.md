# friendsandmountains
Event registration website built with django

## Example website
[Friends and Mountains](http://friends-and-mountains.ch/)

## Features
- Display past and future events
- Event with pre-defined data model, matching a "camp" event format
- Use markdown format for the description
- Manage all events in the django admin panel
- Open and close the registrations as you want
- Add daily program to the event
- Add multiple photos as a gallery to each event
- Event registration form: Register yourself and max. 1 friend
- Payment integration with stripe
- Mailing automation integration with sender.net
- XLS and CSV download of registered participants from the django admin panel

## How to use for your own events
I built this website to make event organization for mountain weekends, birthdays etc easier.  
Feel free to contribute, fork, or contact me to use it for your own event.

---

## Deploy this website (example: pythonanywhere)
A django website is not as easy to deploy as wordpress, for example. What works well for me is with pythonanywhere.com and a mySQL database:

For a complete step-by-step guide, check out the official PythonAnywhere documentation:
[How to deploy a Django web app with PythonAnywhere](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)

In the web app section, you have to add both the statics and the media folder:

| URL | Directory |
| --- | --- |
| /static/ | /home/yourname/friendsandmountains/fnm/staticfiles |
| /media/ | /home/yourname/friendsandmountains/fnm/media |

Don't forget about these steps:
- Export staticfiles: `python manage.py collectstatic`
- Apply database migrations: `python manage.py migrate`
- Create an `.env` file on your server (see `.env.example` for reference) and add your secrets there
- Create an admin user with `python manage.py createsuperuser`
- If using Stripe, make sure to update your API keys in the `.env` file
