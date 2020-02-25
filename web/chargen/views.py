from django.shortcuts import render

# Create your views here.

from .models import CharApp
from web.chargen.forms import AppForm
from django.http import HttpResponseRedirect
from datetime import datetime
from evennia.objects.models import ObjectDB
from django.conf import settings
from evennia.utils import create

def index(request):
    current_user = request.user # current user logged in
    p_id = current_user.id # the account id
    # submitted Characters by this account
    sub_apps = CharApp.objects.filter(account_id=p_id, submitted=True)
    context = {'sub_apps': sub_apps}
    # make the variables in 'context' available to the web page template
    return render(request, 'chargen/index.html', context)

def detail(request, app_id):
    app = CharApp.objects.get(app_id=app_id)
    name = app.char_name
    background = app.background
    submitted = app.submitted
    p_id = request.user.id
    context = {'name': name, 'background': background, 
        'p_id': p_id, 'submitted': submitted}
    return render(request, 'chargen/detail.html', context)

def creating(request):
    user = request.user
    if request.method == 'POST':
        form = AppForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            background = form.cleaned_data['background']
            applied_date = datetime.now()
            submitted = True
            if 'save' in request.POST:
                submitted = False
            app = CharApp(char_name=name, background=background, 
            date_applied=applied_date, account_id=user.id, 
            submitted=submitted)
            app.save()
            if submitted:
                # Create the actual character object
                typeclass = settings.BASE_CHARACTER_TYPECLASS
                home = ObjectDB.objects.get_id(settings.GUEST_HOME)
                # turn the permissionhandler to a string
                perms = str(user.permissions)  
                # create the character
                char = create.create_object(typeclass=typeclass, key=name, 
                    home=home, permissions=perms)
                user.db._playable_characters.append(char)
                # add the right locks for the character so the account can
                #  puppet it
                char.locks.add("puppet:id(%i) or pid(%i) or perm(Developers) "
                    "or pperm(Developers)" % (char.id, user.id))
                char.db.background = background # set the character background
            return HttpResponseRedirect('/chargen')
    else:
        form = AppForm()
    return render(request, 'chargen/create.html', {'form': form})

def creating(request):
    user = request.user
    if request.method == 'POST':
        form = AppForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            background = form.cleaned_data['background']
            applied_date = datetime.now()
            submitted = True
            if 'save' in request.POST:
                submitted = False
            app = CharApp(char_name=name, background=background, 
            date_applied=applied_date, account_id=user.id, 
            submitted=submitted)
            app.save()
            if submitted:
                # Create the actual character object
                typeclass = settings.BASE_CHARACTER_TYPECLASS
                home = ObjectDB.objects.get_id(settings.GUEST_HOME)
                # turn the permissionhandler to a string
                perms = str(user.permissions)  
                # create the character
                char = create.create_object(typeclass=typeclass, key=name, 
                    home=home, permissions=perms)
                user.db._playable_characters.append(char)
                # add the right locks for the character so the account can
                #  puppet it
                char.locks.add("puppet:id(%i) or pid(%i) or perm(Developers) "
                    "or pperm(Developers)" % (char.id, user.id))
                char.db.background = background # set the character background
            return HttpResponseRedirect('/chargen')
    else:
        form = AppForm()
    return render(request, 'chargen/create.html', {'form': form})