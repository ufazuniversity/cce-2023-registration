import functools

from allauth.account import forms as allauth_forms
from django import forms
from django import utils
from django.conf import settings
from phonenumber_field import widgets as pn_widgets

from . import models


class BootstrapFormControlMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({"class": "form-control"})


@functools.cache
def area_code_choices():
    language = utils.translation.get_language() or settings.LANGUAGE_CODE
    default_choices = pn_widgets.localized_choices(language)
    default_choices.sort(key=lambda item: item[1])
    codes_to_remove = ["AM"]
    choices = [i for i in default_choices if i[0] not in codes_to_remove]
    return choices


class ParticipantForm(forms.ModelForm):
    allergies = forms.CharField(
        label="Allergies (optional)",
        widget=forms.Textarea,
        required=False,
        help_text="Please specify if you have any allergies",
    )
    special_request = forms.CharField(
        label="Special meal request (optional)",
        widget=forms.Textarea,
        required=False,
        help_text="Please specify if you have any special meal request (e.g. vegetarian, vegan, halal, etc.)",
    )

    class Meta:
        model = models.Participant
        exclude = ["order_ticket"]
        widgets = {
            "fullname": forms.TextInput(attrs={"placeholder": "John Doe"}),
            "email": forms.EmailInput(attrs={"placeholder": "john.doe@example.org"}),
            "phone_number": forms.EmailInput(attrs={"placeholder": "+994123456789"}),
        }

    def __init__(self, includes_meal: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({"class": "form-control"})
        if not includes_meal:
            del self.fields["allergies"]
            del self.fields["special_request"]


class StudentParticipantForm(ParticipantForm):
    class Meta(ParticipantForm.Meta):
        model = models.StudentParticipant


# Allauth form modifications


class SignupForm(BootstrapFormControlMixin, allauth_forms.SignupForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "First name"})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Last name"})
    )


class LoginForm(BootstrapFormControlMixin, allauth_forms.LoginForm):
    pass


class ResetPasswordForm(BootstrapFormControlMixin, allauth_forms.ResetPasswordForm):
    pass


class ResetPasswordKeyFrom(
    BootstrapFormControlMixin, allauth_forms.ResetPasswordKeyForm
):
    pass


class SetPasswordForm(BootstrapFormControlMixin, allauth_forms.SetPasswordForm):
    pass


class ChangePasswordForm(BootstrapFormControlMixin, allauth_forms.ChangePasswordForm):
    pass


class AddEmailForm(BootstrapFormControlMixin, allauth_forms.AddEmailForm):
    pass
