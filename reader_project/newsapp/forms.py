from django import forms

class feedLink(forms.Form):
	rssLink=forms.CharField(label='Your RSS Feed', max_length=200, required=False)

class key_search(forms.Form):
    keySearch=forms.CharField(label='', max_length=100)

class filtering(forms.Form):
    keywds=forms.CharField(label='', max_length=1000, required=False)

class resetting(forms.Form):
    rst=1


