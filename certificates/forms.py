from django import forms
from .models import Certificate


class CertificateCreateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = [
            'recipient_name',
            'recipient_email',
            'title',
            'description',
            'issuer_name',
            'issue_date',
            'expiry_date',
        ]
        widgets = {
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom complet du destinataire'
            }),
            'recipient_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemple.com'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Diplôme en Développement Web'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description du certificat...'
            }),
            'issuer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de l\'organisme'
            }),
            'issue_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        issue_date = cleaned_data.get('issue_date')
        expiry_date = cleaned_data.get('expiry_date')

        if issue_date and expiry_date:
            if expiry_date <= issue_date:
                raise forms.ValidationError(
                    "La date d'expiration doit être postérieure à la date d'émission."
                )
        return cleaned_data


class CertificateVerifyForm(forms.Form):
    certificate_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ex: CERT-2505-A1B2C3',
            'autofocus': True,
        }),
        label="Identifiant du certificat"
    )


class CertificateRevokeForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Raison de la révocation...'
        }),
        label="Raison de la révocation"
    )
    confirm = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="Je confirme vouloir révoquer ce certificat de manière irréversible"
    )