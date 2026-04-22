from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile,Post,Likepost,Followers,Comment
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='signin')
def index(request):

    user_d = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_d)

    user_following = Followers.objects.filter(
        follower=user_d
    ).values_list('username', flat=True)

    posts = Post.objects.filter(
        user__username__in=user_following
    ).order_by('-created_at')

    liked_posts = set(
        Likepost.objects.filter(
            username=request.user.username
        ).values_list('post_id', flat=True)
    )

    post_data = []

    for post in posts:
        post_data.append({
            'post': post,
            'profile_img': Profile.objects.get(user=post.user).profileimg.url,
            'is_liked': str(post.id) in liked_posts
        })


    userto_follow = User.objects.exclude(
        username__in=user_following
    ).exclude(
        username=user_d.username
    ).exclude(
        is_superuser=True
    )

    userto_follow_profiles = Profile.objects.filter(
        user__in=userto_follow
    )

    data = {
        'user_profile': user_profile,
        'post_data': post_data,
        'userto_follow_profiles': userto_follow_profiles,
    }

    return render(request, 'index.html', data)

def commentlist(request , post_id):
    cmt=Comment.objects.filter(post_id=post_id)
    cmt_data=[]
    for cmt in cmt:
        p_img=Profile.objects.get(user=cmt.user).profileimg.url
        cmt_data.append({
            'cmt':cmt,
            'p_img':p_img,
        })
    return render(request,'commentlist.html',{'cmt_data':cmt_data})

def coment(request,post_id):
    text=request.POST.get('cmt')
    user=request.user
    if request.method=="POST":
        coment=Comment.objects.create(user=user,text=text,post_id=post_id)
        coment.save()
        return redirect('/')
    else:
        return redirect('/')
    

def like_post(request,post_id):
    username=request.user.username
    post=get_object_or_404(Post,id=post_id)
    likepost_filter=Likepost.objects.filter(username=username,post_id=post_id).first()
    if likepost_filter is None:
        likepost=Likepost.objects.create(username=username,post_id=post_id)
        likepost.save()
        post.no_of_likes=post.no_of_likes+1
        post.save()
        return redirect('/')
    else:
        likepost_filter.delete()
        post.no_of_likes=post.no_of_likes-1
        post.save()
        return redirect('/')
    
def upload(request):
    if request.method=="POST":
        user=User.objects.get(username=request.user.username)
        image=request.FILES.get("post_image")
        text=request.POST.get('post_text')
        if not image and not text:
            return redirect('/')  # or show message
        user_post=Post.objects.create(user=user,image=image,text=text)
        user_post.save()
        return redirect('/')
    else:
        return redirect('/')

def search(request):
    query = request.POST.get('username').strip()
    if query:
        profiles = Profile.objects.filter(user__username__icontains=query)
    else:
        profiles = Profile.objects.none()
    return render(request, 'search.html', {'profiles': profiles, 'query': query})

def profile(request,pk):
    user=User.objects.get(username=pk)
    user_profile=Profile.objects.get(user=user)
    user_posts=Post.objects.filter(user=user)
    user_post_length=len(user_posts)
    follower_c=len(Followers.objects.filter(username=pk))
    following_c=len(Followers.objects.filter(follower=pk))
    f=Followers.objects.filter(username=pk,follower=request.user.username).first()
    if f:
        button_txt='Unfollow'
    else:
        button_txt='Follow'

    data={'user_profile':user_profile,
          'user_posts':user_posts,
          'user_post_length':user_post_length,
          'follower_c':follower_c,
          'following_c':following_c,
          'button_txt':button_txt
          }
    
    return render(request, 'profile.html',data)

def follower(request):
    if request.method=="POST":
        follower=request.POST.get('follower')
        username=request.POST.get('username')
        follow_filter=Followers.objects.filter(username=username,follower=follower).first()
        if follow_filter is None:
            follow=Followers.objects.create(username=username,follower=follower)
            follow.save()
            return redirect('/profile/'+username)
        else:
            follow_filter.delete()
            return redirect('/profile/'+username)
    else:
        return redirect('/')

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password1 = request.POST.get('password1')

        # 1. Empty field check (MUST be first)
        if not username or not email or not password or not password1:
            messages.info(request, "All fields are required")
            return redirect('signup')

        # 2. Password match check
        if password != password1:
            messages.info(request, "Password didn't match.")
            return redirect('signup')

        # 3. Email exists check
        if User.objects.filter(email=email).exists():
            messages.info(request, "Email already exists")
            return redirect('signup')

        # 4. Username exists check
        if User.objects.filter(username=username).exists():
            messages.info(request, "Username already exists")
            return redirect('signup')

        # 5. Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # 6. Login user
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

        # 7. Create profile
        Profile.objects.create(user=user, id_user=user.id)

        return redirect('setting')

    return render(request, 'signup.html')

def signin(request):
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('/')
        else:
            messages.info(request,"Invalid Credentials")
    return render(request, 'signin.html')

@login_required(login_url='signin')
def signout(request):
    logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def setting(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        profileimg = request.FILES.get('profileimg')
        bio = request.POST.get('bio')
        location = request.POST.get('location')
        if profileimg:
            user_profile.profileimg = profileimg
        if bio:
            user_profile.bio = bio
        if location:
            user_profile.location = location
        user_profile.save()
    return render(request, "setting.html", {'user_profile': user_profile})
