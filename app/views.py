from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from .models import User, Post, Comment


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.get(username=username)
            return render(request, "register.html", {
            "message": "Username already taken."
            })
        except Exception:              
            return render(request, "setup.html", {
                "categories": SUBJECTS,
                'email': email,
                'username': username,
                'password': password
            })
    else:
        return render(request, "register.html")


SUBJECTS = [
    'Technology', 'Sports', 'Arts', 'Mathematics','Humanities', 'Science', 'Curiosity', 'Self-improvement'
]

#url setup (after register page)------------------
def setup(request):
    if request.method == 'POST':
        avatar = request.POST['avatar']
        bio = request.POST['bio']
        like_subjects = request.POST.getlist('select')

        print(like_subjects)

        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.create_user(username, email, password, avatar=avatar, bio=bio, like_subjects=like_subjects)
        login(request, user)
        return HttpResponseRedirect(reverse('index'))
    return Http404('Post method')


#url index ---------------------------------------
def get_popular_user_posts(user):
    fs = user.userprofile.followed_by.all()
    follows = [f.user for f in fs]
    return Post.objects.filter(poster__in=follows)[:4]


def get_popular_posts():
    return Post.objects.order_by('-likes').all()[:3]

def get_top_post():
    return Post.objects.order_by('-likes', '-timestamp').all()[0]

def get_featured_posts():
    return Post.objects.order_by('-likes', '-timestamp').all()[:8]

def is_similar(stuff, search):
    if stuff.lower() == search.lower():
        return True
    count = 0
    for c in stuff.lower():
        if c in search.lower():
            count += 1
    if count == len(stuff):
        return True
    
    return False


def get_basics(title):
    return {
        'title': title,    
        'popular_posts': get_popular_posts(),
        'top_post': get_top_post(),
        'subjects': SUBJECTS,
        'featured_posts': get_featured_posts()
    }

def get_post_from_like_subjects(subjects):
    dic = {}
    for sub in subjects:
        posts = Post.objects.filter(subject=sub).all()[:4]
        dic[sub] = posts
    print(dic)
    return dic



def index(request):
    if request.method == 'POST':
        search = request.POST['q']

        list_search = []
        for p in Post.objects.all():
            if len(list_search) == 5:
                break
            if is_similar(p.title, search):
                list_search.append(p)
        
        users_search = []
        for u in User.objects.all():
            if len(users_search) == 5:
                break
            if is_similar(u.username, search):
                users_search.append(u)

        props = get_basics('SEARCH: '+search)
        props['search'] = True
        props['user_posts'] = list_search
        props['user_search'] = users_search

        return render(request, "index.html", props)

    props = get_basics('POSTS')
    props['like_subs'] = get_post_from_like_subjects(request.user.like_subjects)
    
    if len(request.user.userprofile.followed_by.all()) > 0:
        props['user_posts'] = get_popular_user_posts(request.user)    
        
    return render(request, "index.html", props)

#url compose ------------------------------------
def compose(request):
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        body = request.POST['body']
        subject = request.POST['select']
        sub_subject = request.POST['sub_subject']
        img = request.POST['img']

        new_post = Post(title=title, poster=request.user, subject=subject, sub_subject=sub_subject, content=body, likes=0, description=description, image=img)
        new_post.save()

        return HttpResponseRedirect(reverse('post_view', args=[new_post.id]))


    return render(request, 'compose.html', {
        "categories": SUBJECTS
    })



# url post_view---------------------------------------------
# View for single post

def isSaved(post, user):
    return True if post in user.saved_posts.all() else False

def saveUnsave(post, user):
    try:
        if isSaved(post, user):
            return "unsave"
        else:
            return 'save'
    except User.DoesNotExist:
        return ""

def save_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if isSaved(post, request.user):
        request.user.saved_posts.remove(post)
        print('unsaved!!')
    else:
        request.user.saved_posts.add(post)
        print('saved!!')
    
    return HttpResponseRedirect(reverse('post_view', args=[post.id]))



def initializePostView(post, user):
    c = {
        'post': post,
        'save_unsave': saveUnsave(post, user),
        'comments': post.comments.all(),
    }
    return c

def post_view(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        c = initializePostView(post, request.user)
        t = 'post_view.html'

    except Post.DoesNotExist:
        return render(request, 'nopage.html')

    if request.method == 'POST':
        content = request.POST['replyForm-mess']

        comment = Comment(owner=request.user, content=content)
        comment.save()

        post = Post.objects.get(pk=post_id)
        post.comments.add(comment)
        
        return render(request, t, c)

    return render(request, t, c)


#url post_edit----------------------------------------
def post_edit(request, post_id):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        body = request.POST['body']
        subject = request.POST['select']
        sub_subject = request.POST['sub_subject']
        img = request.POST['img']

        edited = Post.objects.get(id=post_id)

        edited.title=title
        edited.subject=subject
        edited.sub_subject=sub_subject
        edited.content=body
        edited.description=description
        edited.image=img      

        edited.save()  

        return HttpResponseRedirect(reverse('post_view', args=[post_id]))
        

    return render(request, 'compose.html', {
    'edit': True,
    'post': Post.objects.get(id=post_id),
    "categories": SUBJECTS

    })

def post_delete(request, post_id):
    Post.objects.get(id=post_id).delete() 

    messages.info(request, "Post deleted successfully")
    return HttpResponseRedirect(reverse('index'))


#url following---------------------------------------

def isFollowing(online, user):
    if online.userprofile not in user.userprofile.follows.all():
        return False
    else:
        return True

def isFollowingString(online, user):
    if isFollowing(online, user):
        return "Unfollow"
    return "Follow"


def getPostsFromFollowing(user):
    fs = user.userprofile.followed_by.all()
    follows = [f.user for f in fs]
    return Post.objects.filter(poster__in=follows)



def follow(request, user_id):
    user = User.objects.get(id=user_id)
    online = request.user

    if not isFollowing(online, user):
        user.userprofile.follows.add(online.userprofile)
    else:
        user.userprofile.follows.remove(online.userprofile)
    return HttpResponseRedirect(reverse("profile", args=[user]))



#url profile ----------------------------------------
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, 'nopage.html')
    
    string = ''
    for i in request.user.like_subjects:
        string += i
        string += ', '


    posts = Post.objects.filter(poster=user)
    return render(request, "profile.html", {
        "username": user,
        'like_subjects': string,
        'posts_count': len(posts), 
        "posts": posts,
        "followers_count": len(user.userprofile.follows.all()),
        "following_count": len(user.userprofile.followed_by.all()),
        "follow_unfollow": isFollowingString(request.user, user),
        "subjects": SUBJECTS,
        "featured_posts": get_featured_posts(),
        "popular_posts": get_popular_posts()
    })



#url subject ----------------------------------------
def subject_view(request, subject):
    props = get_basics(subject.capitalize())
    props['user_posts'] = Post.objects.filter(subject=subject).order_by('-timestamp').all()[:10]
    return render(request, "index.html", props)

#url feed ----------------------------------------
def get_posts_from_following(user):
    fs = user.userprofile.followed_by.all()
    follows = [f.user for f in fs]
    return Post.objects.filter(poster__in=follows)[:8]


def feed(request):
    props = get_basics('RECOMENDED')
    props['feed'] = True
    props['followings'] = request.user.userprofile.followed_by.all()
    props['user_posts'] = get_posts_from_following(request.user)

    return render(request, "index.html", props)

    
#url saved ----------------------------------------
def saved(request):
    props = get_basics('SAVED POSTS')
    props['user_posts'] = request.user.saved_posts.all()

    return render(request, "index.html", props)