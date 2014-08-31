from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm


def index(request):
    context = RequestContext(request)

    # query db for a list of all categories stored
    category_list = Category.objects.order_by('likes')[:5]
    context_dict = {'categories': category_list}

    # create url attribute for each category
    for category in category_list:
        category.url = category.name.replace(' ', '_')

    # query db for a list of all categories, ordered by views
    category_list_viewed = Category.objects.order_by('-views')[:5]
    context_dict['categories_viewed'] = category_list_viewed
    # create url for each
    for category in category_list_viewed:
        category.url = category.name.replace(' ', '_')

    # obtain our response object early so that we can add cookie info
    response = render_to_response('rango/index.html', context_dict, context)

    if request.session.get('last_visit'):
        last_visit = request.session.get('last_visit')
        visits = request.session.get('visits', 0)

        last_visit_time = datetime.strptime(last_visit[:-7],
                                            "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).days > 0:
            request.session['visits'] = visits + 1
            request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1

    return response

def about(request):
    context = RequestContext(request)
    context_dict = {
        'message': 'Here is the about page',
        'visit_count': request.session.get('visits', 0)
    }
    return render_to_response('rango/about.html', context_dict, context)


def category(request, category_name_url):
    # request our context from the context passed to us
    context = RequestContext(request)
    context_dict = {}

    # change underscores in the category name to spaces
    category_name = category_name_url.replace('_', ' ')

    try:
        # try find a category with given name
        category = Category.objects.get(name=category_name)

        # get all associated pages
        pages = Page.objects.filter(category=category)

        # add results to context
        context_dict['pages'] = pages

        # add category object too
        context_dict['category'] = category
        context_dict['category_name_url'] = encode_url(category_name)
    except Category.DoesNotExist as e:
        pass

    # go to render the response and return it to the client
    return render_to_response('rango/category.html', context_dict, context)


@login_required
def add_category(request):
    # get context from request
    context = RequestContext(request)

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # check if form is valid
        if form.is_valid():
            # save new category to db
            form.save(commit=True)

            # now call the index() view
            # the user will be shown the homepage
            return index(request)
        else:
            # form had errors
            print form.errors
    else:
        # non-POST requests should display form to user
        form = CategoryForm()

    # bad form (or form details), no form supplied...
    # render form with error messages (if any)
    return render_to_response(
        'rango/add_category.html', {'form': form}, context)


@login_required
def add_page(request, category_name_url):
    context = RequestContext(request)

    category_name = decode_url(category_name_url)

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form is not None and form.is_valid():
            page = form.save(commit=False)

            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                # category doesn't exist
                return render_to_response(
                    'rango/add_category.html', {}, context)

            # default value for no. of views
            page.views = 0

            page.save()

            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    return render_to_response(
        'rango/add_page.html',
        {'category_name_url': category_name_url,
         'category_name': category_name, 'form': form},
        context)


def register(request):
    context = RequestContext(request)

    # to check if registration was successful
    registered = False

    # process form data if it's POST
    if request.method == 'POST':
        # grab info from form (both UserForm & UserProfileForm)
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # if both are valid
        if user_form.is_valid() and profile_form.is_valid():
            # save user form data to db
            user = user_form.save()

            # hash password and update
            user.set_password(user.password)
            user.save()

            # now UserProfile instance
            profile = profile_form.save(commit=False)
            profile.user = user

            # if user provided profile pic, get it from input form
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # save the instance
            profile.save()

            # registraton was successful
            registered = True
        else:
            print user_form.errors, profile_form.errors
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response(
        'rango/register.html',
        {
            'user_form': user_form,
            'profile_form': profile_form,
            'registered': registered
        },
        context
    )


def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse('Your Rango account is disabled')
        else:
            print "Invalid login details: {0} {1}".format(username, password)
            return HttpResponse("Invalid login credentials provided")
    else:
        return render_to_response('rango/login.html', {}, context)


@login_required
def user_logout(request):
    logout(request)

    # take user back to login page
    return HttpResponseRedirect('/rango/')


@login_required
def restricted(request):
    return render_to_response("rango/restricted.html", {
        "message": "Since you're logged in, you can see this text!"},
        RequestContext(request))


def decode_url(encoded_url):
    return encoded_url.replace('_', ' ')


def encode_url(decoded_url):
    return decoded_url.replace(' ', '_')
