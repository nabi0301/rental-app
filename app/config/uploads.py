import os
from flask import current_app

# Upload folder configuration
UPLOAD_FOLDER = os.path.join(current_app.root_path, 'static/uploads')
current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
