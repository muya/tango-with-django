from django import forms
from rango.models import Page, Category


class CategoryForm(forms.ModelForm):
    """Handle form for Category model"""
    name = forms.CharField(max_length=128,
                           help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    # an inline class to provide additional info on the form
    class Meta:
        # provide an association between the ModelForm and a model
        model = Category


class PageForm(forms.ModelForm):
    """Handle form for Page model"""
    title = forms.CharField(max_length=128,
                            help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200, help_text="Enter URL of page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Page

        # only show required fields
        fields = ('title', 'url', 'views')

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        # if url is not empty and doesn't start with 'http://' or 'https://',
        # prepend http://
        if (url and not url.startswith('http://')
                and not url.startswith('https://')):
            url = 'http://' + url
            cleaned_data['url'] = url

        return cleaned_data
