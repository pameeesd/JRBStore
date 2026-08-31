import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from storeApp.models import Categoria, Producto


class ProductoForm(forms.ModelForm):
    codigoBarra = forms.CharField(
        max_length=12,
        min_length=12,
        required=True,
        label='Código de barras',
        widget=forms.TextInput(attrs={'class': 'inputoe', 'placeholder': 'Ej. 123456789012'}),
        error_messages={'required': 'El código de barras es obligatorio.'}
    )
    nombre = forms.CharField(
        max_length=100,
        required=True,
        label='Nombre del producto',
        widget=forms.TextInput(attrs={'class': 'inputoe'}),
        error_messages={'required': 'El nombre del producto es obligatorio.'}
    )
    precio = forms.IntegerField(
        min_value=1,
        required=True,
        label='Precio (CLP)',
        widget=forms.NumberInput(attrs={'class': 'inputoe'}),
        error_messages={'required': 'El precio es obligatorio.'}
    )
    stock = forms.IntegerField(
        min_value=0,
        max_value=100,
        required=True,
        label='Stock (0-100)',
        widget=forms.NumberInput(attrs={'class': 'inputoe'}),
        error_messages={'required': 'El stock es obligatorio.'}
    )
    descripcion = forms.CharField(
        max_length=500,
        required=True,
        label='Descripción',
        widget=forms.Textarea(attrs={'class': 'inputoe', 'rows': 3}),
        error_messages={'required': 'La descripción es obligatoria.'}
    )
    foto = forms.ImageField(
        required=False,
        label='Foto del producto',
        widget=forms.FileInput(attrs={'class': 'inputoe', 'accept': '.jpg,.jpeg,.png'})
    )

    class Meta:
        model = Producto
        fields = ['codigoBarra', 'nombre', 'categoria', 'precio', 'stock', 'descripcion', 'foto']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'inputoe'}),
        }

    def clean_codigoBarra(self):
        codigo = self.cleaned_data.get('codigoBarra', '').strip()
        if not codigo:
            raise ValidationError("El código de barras es obligatorio.")
        if len(codigo) != 12 or not codigo.isdigit():
            raise ValidationError("El código de barras debe tener exactamente 12 dígitos numéricos.")
        qs = Producto.objects.filter(codigoBarra=codigo)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Este código de barras ya está registrado.")
        return codigo

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise ValidationError("El nombre del producto es obligatorio.")
        if len(nombre) > 100:
            raise ValidationError("El nombre no puede exceder 100 caracteres.")
        return nombre

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is None or precio <= 0:
            raise ValidationError("El precio debe ser un número entero positivo.")
        return precio

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is None or stock < 0 or stock > 100:
            raise ValidationError("El stock debe estar entre 0 y 100.")
        return stock

    def clean_descripcion(self):
        desc = self.cleaned_data.get('descripcion', '').strip()
        if not desc:
            raise ValidationError("La descripción es obligatoria.")
        if len(desc) > 500:
            raise ValidationError("La descripción no puede exceder 500 caracteres.")
        return desc

    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        if not foto and not (self.instance and self.instance.pk and self.instance.foto):
            raise ValidationError("La foto del producto es obligatoria.")
        if foto:
            ext = foto.name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                raise ValidationError("Únicamente se permiten imágenes con extensión .jpg, .jpeg o .png.")
            if foto.size > 5 * 1024 * 1024:
                raise ValidationError("La imagen no debe pesar más de 5 MB.")
            try:
                from PIL import Image
                img = Image.open(foto)
                img.verify()
                if img.format.lower() not in ['jpeg', 'png']:
                    raise ValidationError("El archivo no es una imagen JPG o PNG válida.")
            except Exception:
                raise ValidationError("El archivo subido no es una imagen válida.")
        return foto


class CategoriaForm(forms.ModelForm):
    codigo = forms.CharField(
        max_length=12,
        min_length=12,
        required=True,
        label='Código',
        widget=forms.TextInput(attrs={'class': 'inputoe', 'placeholder': 'Ej. 123456789012'}),
        error_messages={'required': 'El código de la categoría es obligatorio.'}
    )
    categoria = forms.CharField(
        max_length=20,
        required=True,
        label='Categoría',
        widget=forms.TextInput(attrs={'class': 'inputoe'}),
        error_messages={'required': 'El nombre de la categoría es obligatorio.'}
    )
    subcategoria = forms.CharField(
        max_length=20,
        required=True,
        label='Subcategoría',
        widget=forms.TextInput(attrs={'class': 'inputoe'}),
        error_messages={'required': 'El nombre de la subcategoría es obligatorio.'}
    )

    class Meta:
        model = Categoria
        fields = ['codigo', 'categoria', 'subcategoria']

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo', '').strip()
        if not codigo:
            raise ValidationError("El código de la categoría es obligatorio.")
        if len(codigo) != 12 or not codigo.isdigit():
            raise ValidationError("El código debe contener exactamente 12 dígitos numéricos.")
        qs = Categoria.objects.filter(codigo=codigo)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Este código de categoría ya está registrado.")
        return codigo

    def clean_categoria(self):
        cat = self.cleaned_data.get('categoria', '').strip()
        if not cat:
            raise ValidationError("El nombre de la categoría es obligatorio.")
        if len(cat) > 20:
            raise ValidationError("El nombre de la categoría no puede exceder 20 caracteres.")
        return cat

    def clean_subcategoria(self):
        sub = self.cleaned_data.get('subcategoria', '').strip()
        if not sub:
            raise ValidationError("El nombre de la subcategoría es obligatorio.")
        if len(sub) > 20:
            raise ValidationError("El nombre de la subcategoría no puede exceder 20 caracteres.")
        return sub

    def clean(self):
        cleaned_data = super().clean()
        cat = cleaned_data.get('categoria')
        sub = cleaned_data.get('subcategoria')
        if cat and sub:
            qs = Categoria.objects.filter(categoria__iexact=cat, subcategoria__iexact=sub)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Ya existe esta combinación de Categoría y Subcategoría.")
        return cleaned_data
 

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