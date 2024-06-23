from django.shortcuts import render , redirect
from .models import Blog, Campaign, Replies
from django.utils.timezone import now
from .forms import BlogForm ,CampaignForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required


# Create your views here.
def index(request):
    q= request.GET.get('q') if request.GET.get('q')!=None else ''
    blogs=Blog.objects.filter(Q(author__username__icontains=q)|
                              Q(title__icontains=q)|
                              Q(content__icontains=q)|
                              Q(tags__icontains=q)|
                              Q(blog_type__icontains=q)|
                              Q(campaign_id__name__icontains=q)
                              )
    campaigns = Campaign.objects.all()
    context={"blogs":blogs,"campaigns":campaigns}
    return render(request, "blog/home.html",context)

def blog_detail(request,blog_id):
    blog=Blog.objects.get(blog_id=blog_id)
    replies=Replies.objects.filter(blog_id=blog_id)
    
    if request.user.is_authenticated:
        if request.method == "POST":
            content = request.POST['content']
            
            Replies.objects.create(
                blog_id=blog,
                content=content,
                sender=request.user,
                time_stamp=now(),
            )
            return redirect('blog:blog_detail', blog_id=blog.blog_id)
        
    context={"blog":blog,"replies":replies}
    return render(request,'blog/blog_detail.html',context)

@login_required
def blog_create(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user  
            blog.save()
            return redirect('blog:index') 
    else:
        form = BlogForm()

    return render(request, 'blog/blog_form.html', {'form': form})

@login_required
def blog_update(request,blog_id):
    blog=Blog.objects.get(blog_id=blog_id)
    form=BlogForm(instance=blog)
    if(request.method)=='POST':
        form=BlogForm(request.POST,request.FILES,instance=blog)
        if form.is_valid:
            form.save()
            return redirect('blog:index')   
    context={'form':form}
    return render(request,'blog/blog_form.html',context)
   
@login_required
def blog_delete(request,blog_id):
    obj=Blog.objects.get(blog_id=blog_id)
    if request.method == "POST":
        obj.delete()
        return redirect('blog:index')
    context={'obj':obj}
    return render(request,'blog/delete.html',context)


def campaign_detail(request, campaign_id):
    campaign = Campaign.objects.get(campaign_id=campaign_id)
    return render(request, 'blog/campaign_detail.html', {'campaign': campaign})

@login_required
def campaign_create(request):
    form=CampaignForm()
    if (request.method)=='POST':
        form=CampaignForm(request.POST)   
        if form.is_valid():
            form.save()
            return redirect('blog:index')
    context={'form':form}
    return render(request,'blog/campaign_create.html',context)


@login_required
def campaign_update(request, campaign_id):
    campaign = Campaign.objects.get(campaign_id=campaign_id)
    form=CampaignForm(instance=campaign)
    if(request.method)=='POST':
        form=CampaignForm(request.POST,instance=campaign)
        if form.is_valid:
            form.save()
            return redirect('blog:index')  
        
    return render(request, 'blog/campaign_create.html', {'form': form})

@login_required
def campaign_delete(request, campaign_id):
    obj = Campaign.objects.get(campaign_id=campaign_id)
    if request.method == "POST":
        obj.delete()
        return redirect('blog:index')
    return render(request, 'blog/delete.html', {'obj': obj})

@login_required
def reply_delete(request, reply_id):
    reply = Replies.objects.get(reply_id=reply_id)
    blog_id = reply.blog_id.blog_id
    
    if request.user != reply.sender:
        return redirect('blog:blog_detail', blog_id=blog_id)
    
    if request.method == "POST":
        reply.delete()
        return redirect('blog:blog_detail', blog_id=blog_id)
    return render(request, 'blog/delete.html', {'reply': reply})