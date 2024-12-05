from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile,Post,Likepost,Followers,Comment
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='signin')
def index(request):
    # Get the currently logged-in user
    user_d = User.objects.get(username=request.user.username)
    
    # Get the logged-in user's profile
    user_profile = Profile.objects.get(user=user_d)
    
    # Get the usernames of users the current user is following
    user_following = Followers.objects.filter(follower=user_d).values_list('username', flat=True)
    
    # Get the posts created by the users being followed
    posts = Post.objects.filter(user__username__in=user_following).order_by('-created_at')
    
    # Prepare post data with profile image for each post
    post_data = []
    for post in posts:
        profile_img = Profile.objects.get(user=post.user).profileimg.url
        post_data.append({
            'post': post,
            'profile_img': profile_img
        })
    
    # Get users to suggest for following (exclude already followed users, self, and superuser)
    userto_follow = User.objects.exclude(username__in=user_following).exclude(username=user_d.username).exclude(is_superuser=True)
    userto_follow_profiles = Profile.objects.filter(user__in=userto_follow)
    
    # Prepare data to send to the template
    data = {
        'user_profile': user_profile,          # Logged-in user's profile
        'post_data': post_data,                # Posts with profile images
        'userto_follow_profiles': userto_follow_profiles,  # Suggested users with profiles
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
    if request.method=="POST":
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        password1=request.POST['password1']
        if password==password1:
            if User.objects.filter(email=email).exists():
                messages.info(request,'Email Already Exists')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request,"Username already exists")
                return redirect('signup')
            else:
                user=User.objects.create_user(username=username,email=email,password=password1)
                user.save()
                user=authenticate(username=username,password=password)
                login(request,user)
                #saving user and creating new profile accordingly
                user_model=User.objects.get(username=username)
                new_profile=Profile.objects.create(user=user_model,id_user=user_model.id)
                new_profile.save()
                return redirect('setting')
        else:
            messages.info(request, "Password didn't match.")
            return redirect('signup')
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
