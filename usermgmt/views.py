from django.http import HttpResponseRedirect
from django.views.generic.list_detail import object_list
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from usermgmt.forms import UserProfileForm, ContactForm
from usermgmt.models import *
from tagging.models import Tag, TaggedItem

@login_required
def user_home(request):
    if request.user.profile_set.count() == 1:
        return render_to_response("registration/profile.html", context_instance=RequestContext(request, {'thisuser': request.user, 'profile': request.user.get_profile()}))
    else:
        request.user.message_set.create(message="<span class=\"error\">Please create a user profile</span>")
        return HttpResponseRedirect('/accounts/profile/edit/')

@login_required
def user_view(request, username):
    userprofile = get_object_or_404(Profile, user__username__exact = username)
    return render_to_response("registration/profile.html", context_instance=RequestContext(request, {'profile': userprofile}))

@login_required
def user_edit(request):
    if (request.method == "POST"):
        if (request.user.profile_set.count()):
            form = UserProfileForm(request.POST, instance=request.user.get_profile())
        else:
            form = UserProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit = False)
            profile.user = request.user
            profile.save
            form.save_m2m()
            profile.save()
            request.user.message_set.create(message="<span class=\"success\">Information successfully updated!</span>")
            return HttpResponseRedirect('/accounts/profile/')
        else:
            return render_to_response("registration/profile_form.html", context_instance=RequestContext(request, {'form': form}))
    else:
        if (request.user.profile_set.count()):
            profile = UserProfileForm(instance=request.user.get_profile())
        else:
            profile = UserProfileForm()
        return render_to_response("registration/profile_form.html", context_instance=RequestContext(request, {'form': profile}))

def with_tags(request, tag, object_id = None, page = 1):
    tag = tag.replace('-', ' ')
    query = Tag.objects.get(name = tag)
    userprofiles = TaggedItem.objects.get_by_model(Profile, query)
    paginate = request.GET.get('paginate_by', None) or 25
    return object_list(request, queryset = userprofiles, paginate_by = int(paginate), template_object_name = "profile", template_name = 'registration/with_tag.html', extra_context = {'tag': tag, 'request': request, 'user': request.user, 'paginate_by': int(paginate)})

def contact(request):
    form = None
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            from django.core.mail import send_mail
            subject = "Contact form: " + form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            recipients = ['mjs@mjs-publishing.com']
            send_mail(subject, message, sender, recipients)
            return render_to_response('registration/contact_done.html', context_instance=RequestContext(request))
        else:
            errors = True
    else:
        errors = False
        form = ContactForm({'sender': request.user.is_authenticated() and request.user.email or ''})
    return render_to_response('registration/contact_form.html', context_instance=RequestContext(request, {'form': form, 'errors': errors}))
