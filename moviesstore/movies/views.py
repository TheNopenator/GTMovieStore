from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Petition, Vote
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    
    # Define rating hierarchy
    rating_order = {'G': 0, 'PG': 1, 'PG-13': 2, 'R': 3}
    
    # Filter movies based on user's max content rating
    restricted_movie_ids = []
    if request.user.is_authenticated:
        user_profile = request.user.profile
        max_rating_value = rating_order.get(user_profile.max_content_rating, 3)
        restricted_movie_ids = [m.id for m in movies if rating_order.get(m.rating, 3) > max_rating_value]
    
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    template_data['restricted_movie_ids'] = restricted_movie_ids
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie, reported=False)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.reported = True
    review.save()
    return redirect('movies.show', id=id)

def petition_list(request):
    """Display all movie petitions with vote counts"""
    petitions = Petition.objects.all().order_by('-created_date')
    template_data = {
        'title': 'Movie Petitions',
        'petitions': petitions
    }
    return render(request, 'movies/petition_list.html', {'template_data': template_data})

@login_required
def create_petition(request):
    """Create a new movie petition"""
    if request.method == 'POST':
        movie_title = request.POST.get('movie_title', '').strip()
        description = request.POST.get('description', '').strip()
        
        if movie_title:
            petition = Petition()
            petition.movie_title = movie_title
            petition.description = description
            petition.created_by = request.user
            petition.save()
            messages.success(request, f'Petition for "{movie_title}" created successfully!')
            return redirect('movies.petition_list')
        else:
            messages.error(request, 'Movie title is required.')
    
    template_data = {
        'title': 'Create Movie Petition'
    }
    return render(request, 'movies/create_petition.html', {'template_data': template_data})

@login_required
def vote_petition(request, petition_id):
    """Vote on a petition (add vote)"""
    petition = get_object_or_404(Petition, id=petition_id)
    
    try:
        vote = Vote()
        vote.petition = petition
        vote.user = request.user
        vote.save()
        messages.success(request, f'Your vote for "{petition.movie_title}" has been recorded!')
    except IntegrityError:
        messages.info(request, 'You have already voted on this petition.')
    
    return redirect('movies.petition_list')
