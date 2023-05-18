from django import forms
from .models import certificate_type, certificate

class NewCertificateType(forms.ModelForm):
    document_category = forms.CharField(max_length=50, label=("Document Category"))
    document_identifier = forms.IntegerField(label=("Document Identifier"))
    document_title = forms.CharField(max_length=50, label=("Document Title"))
    document_grade = forms.CharField(max_length=50, label=("Grade"))
    document_score = forms.IntegerField(label=("Score"))
    year_maximum = forms.IntegerField(label=("Year Maximum"))
    document_category.widget.attrs.update({'class':'new-cert-type'})
    document_identifier.widget.attrs.update({'class':'new-cert-type'})
    document_title.widget.attrs.update({'class':'new-cert-type'})
    document_grade.widget.attrs.update({'class':'new-cert-type'})
    document_score.widget.attrs.update({'class':'new-cert-type'})
    year_maximum.widget.attrs.update({'class':'new-cert-type'})

    class Meta:
        model = certificate_type
        fields = ['document_category','document_identifier','document_title','document_grade','document_score','year_maximum']

class select_certificate(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if obj.grade.upper()=='NA':return "%s %s - %s" %(obj.id, obj.category, obj.title)
        return "%s %s - %s: %s" %(obj.id, obj.category, obj.title, obj.grade)

class NewCertificate(forms.ModelForm):
    document_id = select_certificate(queryset=certificate_type.objects.all(),label=("Document Category"))
    document_description = forms.CharField(max_length=150, label=("Document Description"))
    semester = forms.IntegerField(label=("Semester"))
    year = forms.IntegerField(label=("Year"))
    hardcopy = forms.BooleanField(label=("Hardcopy Submitted"), required=False)
    document_id.widget.attrs.update({'class':'new-cert'})
    document_description.widget.attrs.update({'class':'new-cert'})
    semester.widget.attrs.update({'class':'new-cert'})
    year.widget.attrs.update({'class':'new-cert'})
    hardcopy.widget.attrs.update({'class':'new-cert'})

    class Meta:
        model = certificate
        fields = ['document_id','document_description','semester','year','hardcopy']
