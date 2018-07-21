from account.views import LoginView
from django.contrib.auth import authenticate, REDIRECT_FIELD_NAME, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from data_model.utils import get_dataset_from_invite_key
from kono_data.forms import SignUpForm


def signup(request, **kwargs):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.bio = form.cleaned_data.get('bio')
            user.profile.location = form.cleaned_data.get('location')
            user.profile.email = form.cleaned_data.get('email')
            user.save()

            invite_key = kwargs.get('invite_key')
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
    return render(request, 'signup.html', {'form': form})

#
# def login(request, template_name='registration/login.html',
#           redirect_field_name=REDIRECT_FIELD_NAME,
#           authentication_form=AuthenticationForm,
#           extra_context=None, **kwargs):
#     return LoginView.as_view(
#         template_name=template_name,
#         redirect_field_name=redirect_field_name,
#         form_class=authentication_form,
#         extra_context=extra_context,
#     )(request)
