import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
SQLALCHEMY_DATABASE_URI = 'postgresql://mohamed:123@localhost:5432/fyyurdb'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY='bdd66094fe37c7ad8551faf0d0f07a9a5aa23ded64ce0de8ebf5817a16653efd'