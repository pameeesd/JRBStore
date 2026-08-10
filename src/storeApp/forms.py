from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from storeApp.models import Categoria, Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'
        widgets = {
            'codigoBarra': forms.TextInput(attrs={'class':'inputoe'}),
            'nombre': forms.TextInput(attrs={'class':'inputoe'}),
            'categoria' : forms.Select(attrs={'class':'inputoe'}) ,
            'precio': forms.NumberInput(attrs={'class':'inputoe'}),
            'stock': forms.NumberInput(attrs={'class':'inputoe'}),
            'descripcion': forms.Textarea(attrs={'class':'inputoe','rows':3}),
            'foto': forms.FileInput(attrs={'class':'inputoe'})
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = '__all__'
        widgets = {
            'codigo': forms.TextInput(attrs={'class':'inputoe'}),
            'categoria' : forms.TextInput(attrs={'class':'inputoe'})
        } 

class RegistroForm(UserCreationForm):
    nombre = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'inputoe'}))
    
    class Meta:
        model = User
        fields = ('username', 'nombre', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'inputoe'}),
            'email': forms.EmailInput(attrs={'class': 'inputoe'}),
            'password1': forms.PasswordInput(attrs={'class': 'inputoe'}),
            'password2': forms.PasswordInput(attrs={'class': 'inputoe'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'inputoe'})
        self.fields['password2'].widget.attrs.update({'class': 'inputoe'})

    def clean_password2(self):
        password2 = self.cleaned_data.get("password2")
        username = self.cleaned_data.get("username")

        if password2 and username and username in password2:
            raise ValidationError("La contraseña no puede ser similar al nombre de usuario.")

        return super().clean_password2()
 