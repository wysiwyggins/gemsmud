"""
Url definition file to redistribute incoming URL requests to django
views. Search the Django documentation for "URL dispatcher" for more
help.

"""
from django.conf.urls import url, include

# default evennia patterns
from evennia.web.urls import urlpatterns

# eventual custom patterns
custom_patterns = [
    # url(r'/desired/url/', view, name='example'),
]

# this is required by Django.
urlpatterns += [
    url(r'^chargen/', include('web.chargen.urls')),
]

urlpatterns = custom_patterns + urlpatterns
