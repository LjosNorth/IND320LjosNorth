from enum import Enum

# UserRoles
class UserRoles(Enum):
    ADMIN = 3 # Admin
    USER = 2 # Logged-in User
    VIEWER = 1 # Default, visiting the page
