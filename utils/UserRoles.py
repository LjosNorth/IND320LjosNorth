'''
enumeration for userroles
'''

from enum import Enum

# UserRoles
class UserRoles(Enum):
    VIEWER = 1  # Default, visiting the page
    USER = 2 # Logged-in User
    ADMIN = 3 # Admin
    SECRET = 4 # shh im not here
