# to access forms from the main forms/ directory without having to import each form individually
# to access: from core.models import *
# from core.models import Post, Profile, Comment, Voting, Search, Following

from .base_models import *
from .posts_models import *
from .profiles_models import *
from .comments_models import *
from .voting_models import *
from .search_models import *
from .following_models import *
