a simple image gallery to see my collection of STL files.
Based on https://github.com/kkosiba/django-gallery but modified a bit everywhere to fit my needs.

The following notes where made when setting it up from scratch on a freshly flashed raspberry pi 3B+

# requirement
- postgres
- python3
- install requirements.txt (in a venv if you want)
- apt-get install libopenjp2-7 libtiff5

# Setup
quick notes on the setup (with gunicorn and caddyserver)

in cloned repository:
- generate prod djano secret and put it in https://caddyserver.com/docs/install
- setup django user
- setup postgresql database
- change database settings in website/settings/production.py to match django user
- change allow host to match your domain in the same settings
- setup caddy server
- python3 manage.py makemigration --settings=website.settings.production
- python3 manage.py migrate --settings=website.settings.production
- python3 manage.py collectstatic  --settings=website.settings.production

- to test everything is good run `python3 manage.py runserver 0.0.0.0:8000 --settings=website.settings.production` (be sure to have the local IP of the rasp in authurized domain)

- `gunicorn wsgi:application -b 0.0.0.0:8000` should have the same result
- if you want it to start at boot follow https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04#create-a-gunicorn-systemd-service-file
- If you are running on a rasp and plan to upload big zips, you will need to increase the defualt timeout (30s). For example for 5min timeout `--timeout 300`  .

- dowload latest caddy here https://github.com/caddyserver/caddy/releases
- CaddyFile should looke like:
```
domain.name

encode gzip zstd

root * /home/pi/stl_viewer/website/

@notStatic {
  not path /static/* /media/*
}

reverse_proxy @notStatic localhost:8000
file_server
```
- to auto start at boot follow https://caddyserver.com/docs/install

# features
quick notes on the features

- django admin available in /admin if you are superuser

#### Account:

   - an account is needed to see the content
   - Account can be created only in Django admin (/admin)
   - Superuser only can upload new images, change description or tags and delete images

#### View:

- header:
  - login/logout/change password button
  - home button
  - if super user there is a link to upload a zip file
	
- home:
  - list all tags with at least 1 photo tagged, the display image is random amoung the tagged images
  - the first link is  alist all all images
	
- tag view:
  - Tags in the first home links to a tag list view, only images with the clicked tag are listed
  - a user with can_tag permission can tag either listing or picture or both. These permissions has to be set in the django admin
	
- detail view:
  - in detail view you can the description which the path to the stl file in your system (to easily access it if you want to print it)
  - if superuser you have button to edit or delete the images
  - When editing tags, they are autocompleted, putting a non existant tag will creat it automatically

- Upload:
  - just select the zip file to upload and go. If the upload fails a quick description of the problem will be displayed
 
- Search:
  - the content is splitted in token (separated by spaces)
  - the result of the search is the list images where each token is easier a part of the name or a tag of the images
  - this allow to put multiple tags to norrow down a search
  - it also allow to get all images containing a keyword and having some specific tags
  - a taoken starting with a '!' will remove any picture with this token in their name or tags

- Admin:
  - available at /admin
  - default django admin
  - user account has to be created manually here
  - cann add listing.can_tag and gallery.can_tag permission

- Listing:
  - The listing symbols next to the home on switch to the listing view.
  - This view has the same features than the gallery but contains links instead of images.

# upload structure:
- have to be a zip
- have to contain all images to uplaod.
- have to contain a file named "config.json"
- json format:
```[                                                                                                                                                                                                                   
    {                                                                                                                                                                                                               
        "img_name":"file_name_within_zip_file.png",                                                                                                                                                                                              
        "stl_path":"path/to/your/stl/file/file.stl",                                                                                                                                                           
        "tags":"test42,test2,new_test"                                                                                                                                                                              
    }                                                                                                                                                                                                               
]
```

- non-existing tags will be created automatically
- Also it is possible to update tags of an image via the upload feature. For that "img_name" has to be an empty string and "stl_path" has to match with the image you want to add tags. Again missing tags will be created automatically.
- If an picture with the same stl_path exists, it's tag will be updated with the one in the zip and the image will be replaced by the on in the zip
