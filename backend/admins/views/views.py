from .static_translations import *
from .util_views import *
from .base_views import *
from .user_views import *
from .order_view import *
# Create your views here.


# home admin
def home(request):
    return render(request, 'admin/base_template.html')


# test view
def tg_login(request):
    return render(request, "admin/index_test.html")
