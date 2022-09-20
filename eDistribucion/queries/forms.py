import json
from django import forms
from bootstrap5.widgets import RadioSelectButtonGroup
from django.conf import settings

class ChooseForm(forms.Form):
    fecha = forms.ChoiceField(
        help_text="Selecciona el tipo de consulta.",
        required=True,
        label="Tipos de consulta.",
        widget=RadioSelectButtonGroup,
        choices=((1, 'Último día'), (2, 'Última semana'), (3, 'Último mes'), (4, 'Elegir día')),
    )
    
class OnlyDateForm(forms.Form):
    day = forms.DateField(label="Elegir día", widget=forms.DateInput(attrs={'type': 'date'}))

class LoginForm(forms.Form):
    username = forms.CharField(label="Usuario", max_length=100, initial=settings.USER)
    password = forms.CharField(widget=forms.PasswordInput(render_value=settings.PASSWORD), label="Contraseña", max_length=25, initial=settings.PASSWORD)
    
class ChooseCycleForm(forms.Form):
    cycle = forms.ChoiceField()
    
class AdvancedSearchForm(forms.Form):
    start = forms.DateField(label="Fecha inicio", widget=forms.DateInput(attrs={'type': 'date'}))
    end = forms.DateField(label="Fecha fin", widget=forms.DateInput(attrs={'type': 'date'}))
