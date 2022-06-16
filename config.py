
TARGET_DIR="../landing-page-2022/"


####  This is with repsct to the TARGET_DIR ####

import os.path as op

TARGET_DIR = op.abspath(TARGET_DIR)

PUBLIC = op.join(TARGET_DIR, 'public')

DATA = op.join(TARGET_DIR, 'src', 'data')

IMG = op.join(PUBLIC, 'img')
