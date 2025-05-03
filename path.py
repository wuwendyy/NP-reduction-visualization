import os

# Don't change this, this saves you from relative path issues :)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # The directory where this script is located
DATA_DIR = os.path.join(BASE_DIR, 'data')  # Directory for data files
NPVIS_DIR = os.path.join(BASE_DIR, 'npvis')  # Directory for npvis package
TEST_DIR = os.path.join(BASE_DIR, 'tests')  # Directory for tests
