# to access tests from the main tests/ directory without having to import each test individually
# to access: python manage.py test is used as django searches for test_*.py files in the tests/ directory

from .test_base import *
from .test_posts import *
from .test_profiles import *
from .test_comments import *
from .test_voting import *
