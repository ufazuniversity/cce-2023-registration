import functools

from django import forms
from django import utils
from django.conf import settings
from phonenumber_field import widgets as pn_widgets

from . import models


@functools.cache
def area_code_choices():
    language = utils.translation.get_language() or settings.LANGUAGE_CODE
    default_choices = pn_widgets.localized_choices(language)
    default_choices.sort(key=lambda item: item[1])
    codes_to_remove = ["AM"]
    choices = [i for i in default_choices if i[0] not in codes_to_remove]
    return choices


class ParticipantForm(forms.ModelForm):
    allergies = forms.CharField(widget=forms.Textarea, required=False)
    special_request = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = models.Participant
        exclude = ["order_ticket"]

    def __init__(self, includes_meal: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({"class": "form-control"})
        if not includes_meal:
            del self.fields["allergies"]
            del self.fields["special_request"]


class StudentParticipantForm(ParticipantForm):
    class Meta:
        model = models.StudentParticipant
        fields = "__all__"
