from django import forms

from . import models


class ParticipantForm(forms.ModelForm):
    allergies = forms.CharField(widget=forms.Textarea, required=False)
    special_request = forms.CharField(widget=forms.Textarea, required=False)

    # phone_number = pn_fields.PhoneNumberField(region="AZ")

    class Meta:
        model = models.Participant
        exclude = ["order_ticket"]

    def __init__(self, includes_meal: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({'class': 'form-control'})
        if not includes_meal:
            del self.fields["allergies"]
            del self.fields["special_request"]


class StudentParticipantForm(ParticipantForm):
    class Meta:
        model = models.StudentParticipant
        fields = "__all__"
