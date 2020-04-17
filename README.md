a simple image gallery to see my collection of STL files.
Based on https://github.com/kkosiba/django-gallery but modified a it everywhere to fit my needs.

# requirement
postgres
django
install requirements.txt (in a venv if you want)

# Setup
quick notes on the setup (with https and nginx)

in cloned repository:
TODO  setup prod
TODO setup nginx
python3 manage.py makemigration --settings=website.settings.production
python3 manage.py migrate --settings=website.settings.production
python3 manage.py runserver --settings=website.settings.production

# features
quick notes on the features

django admin available in /admin if you are superuser
Account:
	An account is needed to see the content
	Account can be created only in Django admin
	Superuser only can upload new images, change description or tags and delete images

view:
	header:
		login/logout/chqnge password button
		home button
		if super user, link to upload
		search bar
	home:
		list all tags with at least 1 photo tagged, the display image is random amoung the tagged images
		the first link is  alist all all images
	tag:
		Tags in the first home links to a tag list view, only images with the clicked tag are listed
	detail view:
	       in detail view you can the description which the path to the stl file in your system (to easily access it if you want to print it)
	       if superuser you have button to edit or delete the images
	       When editing tags, they are autocompleted, putting a non existant tag will creat it automatically

	upload:
		just select the zip file to upload and go. If the upload fails a quick description of the problem will be displayed

	search:
		the content is splitted in token (separated by spaces)
		the result of the search is the list images where each token is easier a part of the name or a tag of the images
		this allow to put multiple tags to norrow down a search
		it also allow to get all images containing a keyword and having some specific tags 

# upload structure:
have to be a zip
have to contain all images to uplaod.
have to contain a file named "config.json"
json format:
[                                                                                                                                                                                                                   
    {                                                                                                                                                                                                               
        "img_name":"file_name_within_zip_file.png",                                                                                                                                                                                              
        "stl_path":"path/to/your/stl/file/file.stl",                                                                                                                                                           
        "tags":"test42,test2,new_test"                                                                                                                                                                              
    }                                                                                                                                                                                                               
] 

non-existing tags will be created automatically
Also it is possible to update tags of an image via the upload feature. For that "img_name" has to be an empty string and "stl_path" has to match with the image you want to add tags. Again missing tags will be created automatically.
