from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

class SearchForm(forms.Form):
    search = forms.CharField(label='', max_length=256, required=False,
                                widget = forms.TextInput(attrs={'placeholder': 'Search', 'class': 'form-control search-form'}))

class SignUpForm(UserCreationForm):
    username = forms.RegexField(regex=r'^[a-z0-9_.-]+$',
                                max_length=30,
                                label=_("Username"),
                                error_messages={'invalid': _("This value may contain only lowercase letters, numbers and ./-/_ characters.")})
    class Meta:
        model = User

        fields = ('username', 'password1', 'password2')
