from django import forms
from .models import Issue, Event


class IssueCreateForm(forms.ModelForm):
    issue_descr = forms.CharField(label="Описание", max_length=Event.MAX_INFO_LEN, widget=forms.Textarea)
    # TODO rewrite
    photo1 = forms.ImageField(required=False, label="Фотография")
    photo2 = forms.ImageField(required=False, label="Фотография")
    photo3 = forms.ImageField(required=False, label="Фотография")

    class Meta:
        model = Issue
        fields = ["name", "category", "want_to_help"]
