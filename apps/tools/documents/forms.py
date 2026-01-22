from django import forms
from .models import Folder, Document, DocumentVersion

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'description', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Folder Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional Description'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }

class DocumentUploadForm(forms.ModelForm):
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control-file'}))
    change_log = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Initial version'}),
        required=False
    )
    
    class Meta:
        model = Document
        fields = ['title', 'description', 'folder', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Document Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'folder': forms.Select(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DocumentVersionForm(forms.ModelForm):
    class Meta:
        model = DocumentVersion
        fields = ['file', 'change_log']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control-file'}),
            'change_log': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What changed in this version?'}),
        }
