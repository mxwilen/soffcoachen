import os
import uuid
import secrets
from flask import url_for, flash, abort
from PIL import Image
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# from models import Restaurant, Review
from flask_login import current_user
from flask_mail import Message


STORAGE_CONTAINER_NAME = 'profile-pictures'


def get_image_path_no_name(app):
    image_path = get_account_url(app) + "/" +  STORAGE_CONTAINER_NAME
    return image_path

def get_account_url(app):
    if not 'AZURE_STORAGEBLOB_RESOURCEENDPOINT' in os.environ:
        # Create LOCAL_USE_AZURE_STORAGE environment variable to use Azure Storage locally. 
        if 'WEBSITE_HOSTNAME' in os.environ or ("LOCAL_USE_AZURE_STORAGE" in os.environ):
            return "https://%s.blob.core.windows.net" % os.environ['STORAGE_ACCOUNT_NAME']
        else:
            print("Using LOCAL storage.")
            return os.path.join(app.root_path, 'local-storage-container')
    else:
        return os.environ['AZURE_STORAGEBLOB_RESOURCEENDPOINT'].rstrip('/')
    

def save_picture(app, form_picture):
    image_data = form_picture

    # Get size.
    size = len(image_data.read())
    image_data.seek(0)

    print("Original image name = " + image_data.filename)
    print("File size = " + str(size))

    if (size > 2048000):
        return flash('Image too big, try another file.', 'danger')

    # Get account_url based on environment
    print("account_url = " + get_account_url(app))

    if not 'AZURE_STORAGEBLOB_RESOURCEENDPOINT' in os.environ:
        if not 'WEBSITE_HOSTNAME' in os.environ or not ("LOCAL_USE_AZURE_STORAGE" in os.environ):
            random_hex = secrets.token_hex(8)
            _, f_ext = os.path.splitext(form_picture.filename)
            picture_fn = random_hex + f_ext
            picture_path = os.path.join(app.root_path, get_account_url(app), picture_fn)
            output_size = (125, 125)
            i = Image.open(form_picture)
            i.thumbnail(output_size)
            i.save(picture_path)

            prev_picture = os.path.join(app.root_path, get_account_url(app), current_user.image_file)
            if os.path.exists(prev_picture) and current_user.image_file != "default.jpg":
                os.remove(prev_picture)
            
            # Returns local path of the storage-container
            return picture_fn

    # Create client
    azure_credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
    blob_service_client = BlobServiceClient(
        account_url = get_account_url(app),
        credential=azure_credential)

    # Get file name to use in database
    image_name = str(uuid.uuid4()) + ".png"
    
    # Create blob client
    blob_client = blob_service_client.get_blob_client(container=STORAGE_CONTAINER_NAME, blob=image_name)
    print("\nUploading to Azure Storage as blob:\n\t" + image_name)

    # Upload file
    blob_client.upload_blob(image_data)

    return image_name


def send_reset_email(user):
    abort(404)
    """
    token = user.get_reset_token()
    msg = Message("Password Reset Request",
                  sender="noreply@demo.com",
                  recipients=[user.email])
    msg.body = f'''To reset your password, vist the following link: {url_for('reset_token', token=token, _externel=True)} 
        If you did not make this request, simply ignore this email and no changes will be made'''
    
    # mail.send(msg)
    print('Token är: ', token)
    """