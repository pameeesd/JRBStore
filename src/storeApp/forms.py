import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

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
    nombre = forms.CharField(
        max_length=50,
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'inputoe'}),
        error_messages={
            'required': 'El nombre es obligatorio.'
        }
    )
    email = forms.EmailField(
        required=True,
        label='Dirección de correo electrónico',
        widget=forms.EmailInput(attrs={'class': 'inputoe'}),
        error_messages={
            'required': 'Ingresa un correo electrónico válido.',
            'invalid': 'Ingresa un correo electrónico válido.'
        }
    )
    
    class Meta:
        model = User
        fields = ('username', 'nombre', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'inputoe'}),
        }
        error_messages = {
            'password_mismatch': 'Las contraseñas no coinciden.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages['password_mismatch'] = 'Las contraseñas no coinciden.'
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['username'].error_messages['required'] = 'El nombre de usuario es obligatorio.'
        self.fields['password1'].widget.attrs.update({'class': 'inputoe'})
        self.fields['password2'].widget.attrs.update({'class': 'inputoe'})
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmación de contraseña'
        self.fields['password1'].error_messages['required'] = 'La contraseña es obligatoria.'
        self.fields['password2'].error_messages['required'] = 'La confirmación de contraseña es obligatoria.'

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        username = username.strip().lower()
        if not username:
            raise ValidationError("El nombre de usuario es obligatorio.")
        if len(username) < 3:
            raise ValidationError("El nombre de usuario debe tener al menos 3 caracteres.")
        if len(username) > 150:
            raise ValidationError("El nombre de usuario no puede exceder 150 caracteres.")
        if not re.match(r'^[a-z0-9@.+_-]+$', username):
            raise ValidationError("El nombre de usuario contiene caracteres no válidos.")
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Este nombre de usuario ya está registrado.")
        return username

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '')
        nombre = nombre.strip()
        if not nombre:
            raise ValidationError("El nombre es obligatorio.")
        if len(nombre) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres.")
        if len(nombre) > 50:
            raise ValidationError("El nombre no puede exceder 50 caracteres.")
        if nombre.isdigit():
            raise ValidationError("El nombre no puede contener únicamente números.")
        return nombre

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        email = email.strip().lower()
        if not email:
            raise ValidationError("Ingresa un correo electrónico válido.")
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("Ingresa un correo electrónico válido.")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1', '')
        if not password1:
            raise ValidationError("La contraseña es obligatoria.")
        if len(password1) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres, una mayúscula y un carácter especial.")
        if not re.search(r'[A-Z]', password1):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password1):
            raise ValidationError("La contraseña debe contener al menos un carácter especial.")
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        username = cleaned_data.get("username")

        if password1 and password2 and password1 != password2:
            if 'password2' in self._errors:
                self._errors['password2'] = ['Las contraseñas no coinciden.']
            else:
                self.add_error("password2", "Las contraseñas no coinciden.")

        if username and password1 and (username in password1.lower() or password1.lower() in username):
            self.add_error("password1", "La contraseña no puede ser similar al nombre de usuario.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['nombre']
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user