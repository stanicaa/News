from django.shortcuts import render
from newsapp.models import news, rss_field, user_filter
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import nltk
import spacy
import datetime


from .forms import feedLink, key_search, filtering, resetting

#global variables
signs=[',', '!', '.', '?', '=', '%', '$', '#', '&', '(', ')', '>', '<', '{', '}', ':', ';', '[', ']', '-', '...']
nlp = spacy.load('en_core_web_sm')
last24=datetime.datetime.now() - datetime.timedelta(days=1)

#global functions
def text_pos(raw):
    doc=nlp(raw)
    sent=[w for w in doc if w.pos_ in ['NOUN', 'PROPN']]
    sent=str(sent)
    sent=sent[1:-1]
    return sent

# Create your views here.

@login_required
def index(request):
    #identifying current user feeds
    current_user=request.user.username
    user_feed=rss_field.objects.filter(created_by=current_user)
    if user_feed:
        ff=[w.feed_link for w in user_feed]
        ff=set(ff)
        feeds=[w for w in ff]
    else:
        template = loader.get_template('newsapp/index_none.html')
        return HttpResponse(template.render({}, request))

    raw=''
    #add the default links in case user selects no link?
    #PROBLEM - the program below has latest_news hold the values from onlye the LAST for iteration. Need anohter variable to keep all the search results, from ALL the LOOPS
    latest_news=[]
    for link in feeds:
        l_news=news.objects.filter(feed_link=link).filter(created_at__gt=last24).order_by('created_at').reverse()
        for b in l_news:
            latest_news.append(b)
            raw+=' '+text_pos(b.title)
    #building the frequency topics
    tokens=nltk.word_tokenize(raw)
    tokens=[w for w in tokens if w not in ["'", ",", "’"]]
    text=nltk.Text(tokens)
    fd=nltk.FreqDist(text)
    fdd=fd.most_common(20)
    list=[]
    for b in fdd:
        list.append(b[0])
    form=key_search(request.GET or None)
    if request.method == 'GET':
        if form.is_valid():
            keyword=form.cleaned_data['keySearch']
            if keyword:
                latest_news=[w for w in latest_news if keyword in w.title]
    #latest_news=latest_news[:10]
    template = loader.get_template('newsapp/index.html')
    context={
        'latest_news': latest_news,
        'list': list,
        'form': form,
            }
    return HttpResponse(template.render(context, request))

@login_required
def my_filter(request):
    #identifying current user feeds
    current_user=request.user.username
    user_feed=rss_field.objects.filter(created_by=current_user)
    if user_feed:
        feeds=[w.feed_link for w in user_feed]
    else:
        template = loader.get_template('newsapp/index_none.html')
        return HttpResponse(template.render({}, request))
    filter_results=[]
    for link in feeds:
        latest_news=news.objects.filter(feed_link=link).order_by('created_at').reverse()
        for bb in latest_news:
            filter_results.append(bb)
    #Getting the user Filter keywords, and buildign the list with the unique words only
    filter_keys=user_filter.objects.filter(owned_by=request.user.username).values_list('keywds')
    keys_string=''
    for f in filter_keys:
        keys_string+=' '+f[0]
    keys_list=keys_string.split()
    keys_list=set(keys_list)
    k_list=[]
    for g in keys_list:
        k_list.append(g)
    #starting to build the list of the titles having the keywords in their titles
    filtered_list=[]
    raw1=''
    for bb in filter_results:
        for bbb in k_list:
            if bbb in bb.title and bb not in filtered_list:
                filtered_list.append(bb)
                raw1+=' '+text_pos(bb.title)
                break
    #Building the frequent topics
    tokens=nltk.word_tokenize(raw1)
    tokens=[w for w in tokens if w not in ["'", ",", "’"]]
    text=nltk.Text(tokens)
    fd=nltk.FreqDist(text)
    fdd=fd.most_common(20)
    list=[]
    for b in fdd:
        list.append(b[0])
    form_f=key_search(request.GET or None)
    if request.method == 'GET':
        if form_f.is_valid():
            keyword=form.cleaned_data['keySearch']
            if keyword:
                filtered_list=[w for w in filtered_list if keyword in w.title]
    #latest_news=latest_news[:10]
    template = loader.get_template('newsapp/myfilter.html')
    context={
        'filtered_list': filtered_list,
        'list': list,
        'form_f': form_f,
            }

    return render(request, 'newsapp/myfilter.html',context)


@login_required
def customize(request):
    #getting new links from the user to build its profile. FIRST FORM
    form=feedLink(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            m=rss_field()
            m.feed_link=form.cleaned_data['rssLink']
            links=rss_field.objects.filter(created_by=request.user.username).values_list('feed_link')
            if m.feed_link not in [w[0] for w in links]:
                m.created_by=request.user.username
                m.save()
                #remove the below. See what else needs to be done. Need to make sure the saved link appears in the User Existing links on the page
                latest_news=news.objects.order_by('created_at').reverse()[:10]
                template = loader.get_template('newsapp/index.html')
                context={'latest_news': latest_news,}
                return render(request, 'newsapp/index.html', {'latest_news':latest_news})
        else:
            messages.error(request, "Error")
    #ADD the OUR SUGGESTIONS FORM
    #ADD the EXISTING FEED LINKS show here, including the ones just added
    existing_feeds=rss_field.objects.filter(created_by=request.user.username).values_list('feed_link')
    if existing_feeds:
        existing_feeds_list=[]
        for i in range(len(existing_feeds)):
            list_feeds_l=existing_feeds[i][0].split()
            for j in range(len(list_feeds_l)):
                existing_feeds_list.append(list_feeds_l[j])
        existing_feeds_unique=set(existing_feeds_list)
    else:
        existing_feeds_unique='No RSS Links set up yet'
    #FILTER - start building it below
    form_filter=filtering(request.POST or None)
    if request.method == 'POST':
        if form_filter.is_valid():
            n=user_filter()
            n.keywds=form_filter.cleaned_data['keywds']
            n.owned_by=request.user.username
            n.save()

    #ADD the view for the EXISTING filter
    existing=user_filter.objects.filter(owned_by=request.user.username).values_list('keywds')
    if existing:
        existing_list=[]
        for i in range(len(existing)):
            list_l=existing[i][0].split()
            for j in range(len(list_l)):
                existing_list.append(list_l[j])
        if existing_list:
            dummy='b'
            existing_unique=set(existing_list)
        else:
            dummy='a'
            existing_unique='No Filter set up yet'
    else:
        dummy='a'
        existing_unique='No Filter set up yet'
    #FILTER RESET - deleting existing filter words
    form_reset=resetting(request.GET)
    if request.method=='GET':
        if form_reset.is_valid():
            user_filter.objects.filter(owned_by=request.user.username).delete()

    context={'form':form, 'form_filter': form_filter, 'form_reset': form_reset, 'existing_unique':existing_unique, 'existing_feeds_unique':existing_feeds_unique, 'dummy':dummy }
    return render(request, 'newsapp/customize.html',context)


