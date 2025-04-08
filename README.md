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

## 🚀 Deployment on Google App Engine

You can host this Django site easily using Google Cloud's App Engine (Standard Environment).

### Prerequisites
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- A Google Cloud Project
- Your Django app is set up with `gunicorn` as the WSGI server

### 1. Prepare App for Deployment
Create a file named `app.yaml` in your Django root (same folder as `manage.py`):

```yaml
runtime: python310
entrypoint: gunicorn friendsandmountains.wsgi

handlers:
- url: /static
  static_dir: static/
- url: /.*
  script: auto
```

Make sure static files are collected:
```bash
python manage.py collectstatic
```

### 2. Deploy to Google App Engine

Initialize App Engine and deploy:

```bash
gcloud init
gcloud app create
gcloud app deploy
```

Once deployed, your site will be live at `https://<your-project-id>.appspot.com`.

---

## 🌐 Set up a Custom Domain

If you have a custom domain (e.g., `friends-and-mountains.ch`), you can point it to your App Engine app.

### 1. Verify Domain Ownership

- Go to [Custom Domains](https://console.cloud.google.com/appengine/domains)
- Add your domain and follow the DNS TXT record instructions to verify it

### 2. Map the Domain

- After verifying, click **"Add Mapping"**
- Choose your subdomain (e.g., `www.friends-and-mountains.ch`)
- Google will show DNS records to set — add them in your domain registrar (e.g. A or CNAME records)

### 3. SSL is Automatic

Google will provide and manage HTTPS for your custom domain. No extra configuration needed.

Once DNS changes propagate (usually within a few minutes to hours), your custom domain will serve the site securely.

---

Enjoy your own event platform 🚀
