from django.shortcuts import render
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .forms import CustomUserCreationForm, CustomErrorList, ProfilePictureForm, MaxContentRatingForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile
@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')
def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(
            request,
            username = request.POST['username'],
            password = request.POST['password']
        )
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.index')
def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html', {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            form.save()
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html',
                {'template_data': template_data})
@login_required
def orders(request):
    template_data = {}
    template_data['title'] = 'Orders'
    template_data['orders'] = request.user.order_set.all()
    return render(request, 'accounts/orders.html', {'template_data': template_data})

@login_required
def profile(request):
    template_data = {}
    template_data['title'] = 'Profile'
    
    # Get or create profile for the user
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Check which form was submitted
        if 'profile_picture' in request.FILES or 'submit_picture' in request.POST:
            form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                template_data['success'] = 'Profile picture updated successfully!'
            template_data['form'] = form
            template_data['rating_form'] = MaxContentRatingForm(instance=profile)
        elif 'max_content_rating' in request.POST or 'submit_rating' in request.POST:
            rating_form = MaxContentRatingForm(request.POST, instance=profile)
            if rating_form.is_valid():
                rating_form.save()
                template_data['success'] = 'Content rating preference updated successfully!'
            template_data['rating_form'] = rating_form
            template_data['form'] = ProfilePictureForm(instance=profile)
        else:
            template_data['form'] = ProfilePictureForm(instance=profile)
            template_data['rating_form'] = MaxContentRatingForm(instance=profile)
    else:
        template_data['form'] = ProfilePictureForm(instance=profile)
        template_data['rating_form'] = MaxContentRatingForm(instance=profile)
    
    template_data['profile'] = profile
    return render(request, 'accounts/profile.html', {'template_data': template_data})