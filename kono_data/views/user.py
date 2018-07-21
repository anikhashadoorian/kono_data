import warnings

from django.contrib.auth import authenticate, REDIRECT_FIELD_NAME, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, login as auth_login,
)
from data_model.utils import get_dataset_from_invite_key
from kono_data.forms import SignUpForm


def signup(request, **kwargs):
    invite_key = kwargs.get('invite_key')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.bio = form.cleaned_data.get('bio')
            user.profile.location = form.cleaned_data.get('location')
            user.profile.email = form.cleaned_data.get('email')
            user.save()

            if invite_key:
                dataset = get_dataset_from_invite_key(invite_key)
                if dataset:
                    dataset.contributors.add(user)

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()

    context = {'form': form}
    if invite_key:
        context['invite_key'] = invite_key

    return render(request, 'signup.html', context)


class CustomLoginView(LoginView):
    invite_key = None

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        auth_login(self.request, form.get_user())
        if self.invite_key:
            dataset = get_dataset_from_invite_key(self.invite_key)
            if dataset:
                dataset.contributors.add(form.get_user())

        return HttpResponseRedirect(self.get_success_url())


def login_url(request, redirect_field_name=REDIRECT_FIELD_NAME,
              authentication_form=AuthenticationForm,
              extra_context=None, redirect_authenticated_user=False,
              invite_key=None, **kwargs):
    return CustomLoginView.as_view(
        template_name='login.html',
        redirect_field_name=redirect_field_name,
        form_class=authentication_form,
        extra_context=extra_context,
        redirect_authenticated_user=redirect_authenticated_user,
        invite_key=invite_key
    )(request)
