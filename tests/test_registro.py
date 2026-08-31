from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class RegistroUsuariosTests(TestCase):
    def setUp(self):
        # Client enforcing CSRF checks by default when enforce_csrf_checks=True
        self.client_csrf = Client(enforce_csrf_checks=True)
        # Regular test client
        self.client = Client()
        self.url = reverse('registrarse')
        self.valid_data = {
            'username': 'usuario_nuevo',
            'nombre': 'Pamela Garcia',
            'email': 'pamela@example.com',
            'password1': 'ClaveSegura123!',
            'password2': 'ClaveSegura123!',
        }

    def _assert_field_error(self, response, field, expected_error):
        self.assertEqual(response.status_code, 200)
        self.assertIn('formulario', response.context)
        form = response.context['formulario']
        field_errors = form.errors.get(field, [])
        self.assertTrue(
            any(expected_error in str(err) for err in field_errors),
            f"Expected error '{expected_error}' in field '{field}'. Actual errors: {field_errors}"
        )

    def test_01_registro_valido(self):
        """TEST 1: Registro válido crea el usuario y retorna status de éxito/redirección."""
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='usuario_nuevo')
        self.assertEqual(user.first_name, 'Pamela Garcia')
        self.assertEqual(user.email, 'pamela@example.com')

    def test_02_username_vacio(self):
        """TEST 2: Username vacío es rechazado con error."""
        data = self.valid_data.copy()
        data['username'] = ''
        response = self.client.post(self.url, data)
        self._assert_field_error(response, 'username', 'El nombre de usuario es obligatorio.')
        self.assertFalse(User.objects.filter(email='pamela@example.com').exists())

    def test_03_username_duplicado_case_insensitive(self):
        """TEST 3: Username duplicado (case-insensitive) es rechazado."""
        User.objects.create_user(username='pamela', email='existente@example.com', password='Password123!')
        data = self.valid_data.copy()
        data['username'] = 'PAMELA'
        response = self.client.post(self.url, data)
        self._assert_field_error(response, 'username', 'Este nombre de usuario ya está registrado.')

    def test_04_nombre_vacio(self):
        """TEST 4: Nombre vacío es rechazado."""
        data = self.valid_data.copy()
        data['nombre'] = '   '
        response = self.client.post(self.url, data)
        self._assert_field_error(response, 'nombre', 'El nombre es obligatorio.')

    def test_05_email_invalido(self):
        """TEST 5: Email inválido es rechazado."""
        data = self.valid_data.copy()
        data['email'] = 'correo-invalido'
        response = self.client.post(self.url, data)
        self._assert_field_error(response, 'email', 'Ingresa un correo electrónico válido.')

    def test_06_email_vacio(self):
        """TEST 6: Email vacío es rechazado."""
        data = self.valid_data.copy()
        data['email'] = ''
        response = self.client.post(self.url, data)
        self._assert_field_error(response, 'email', 'Ingresa un correo electrónico válido.')

    def test_07_password_corta(self):
        """TEST 7: Contraseña menor a 8 caracteres es rechazada."""
        data = self.valid_data.copy()
        data['password1'] = 'Short1!'
        data['password2'] = 'Short1!'
        response = self.client.post(self.url, data)
        self._assert_field_error(response, 'password1', 'La contraseña debe tener al menos 8 caracteres, una mayúscula y un carácter especial.')

    def test_08_password_sin_mayuscula(self):
        """TEST 8: Contraseña sin mayúscula es rechazada."""
        data = self.valid_data.copy()
        data['password1'] = 'clavesegura123!'
        data['password2'] = 'clavesegura123!'
        response = self.client.post(self.url, data)
        self._assert_field_error(response, 'password1', 'La contraseña debe contener al menos una letra mayúscula.')

    def test_09_password_sin_caracter_especial(self):
        """TEST 9: Contraseña sin carácter especial es rechazada."""
        data = self.valid_data.copy()
        data['password1'] = 'ClaveSegura123'
        data['password2'] = 'ClaveSegura123'
        response = self.client.post(self.url, data)
        self._assert_field_error(response, 'password1', 'La contraseña debe contener al menos un carácter especial.')

    def test_10_passwords_diferentes(self):
        """TEST 10: Contraseñas no coincidentes son rechazadas."""
        data = self.valid_data.copy()
        data['password2'] = 'OtraClave123!'
        response = self.client.post(self.url, data)
        self._assert_field_error(response, 'password2', 'Las contraseñas no coinciden.')

    def test_11_password_igual_o_similar_a_username(self):
        """TEST 11: Contraseña igual o muy similar al username es rechazada."""
        data = self.valid_data.copy()
        data['username'] = 'Pamela123'
        data['password1'] = 'Pamela123!'
        data['password2'] = 'Pamela123!'
        response = self.client.post(self.url, data)
        self._assert_field_error(response, 'password1', 'La contraseña no puede ser similar al nombre de usuario.')

    def test_12_strip_espacios_innecesarios(self):
        """TEST 12: Espacios al inicio/final en username, email y nombre son eliminados."""
        data = {
            'username': '   usuario_espacios   ',
            'nombre': '   Carlos Perez   ',
            'email': '   carlos@example.com   ',
            'password1': 'ClaveSegura123!',
            'password2': 'ClaveSegura123!',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='usuario_espacios')
        self.assertEqual(user.first_name, 'Carlos Perez')
        self.assertEqual(user.email, 'carlos@example.com')

    def test_13_post_sin_csrf_rechazado(self):
        """TEST 13: Solicitud POST sin token CSRF es rechazada con HTTP 403."""
        data = self.valid_data.copy()
        response = self.client_csrf.post(self.url, data)
        self.assertEqual(response.status_code, 403)

    def test_14_password_almacenada_con_hash(self):
        """TEST 14: La contraseña en la base de datos se guarda como hash y NUNCA en texto plano."""
        raw_password = 'ClaveSegura123!'
        data = self.valid_data.copy()
        data['password1'] = raw_password
        data['password2'] = raw_password
        self.client.post(self.url, data)
        user = User.objects.get(username='usuario_nuevo')
        
        # Verificar que la contraseña no está en texto plano
        self.assertNotEqual(user.password, raw_password)
        self.assertNotIn(raw_password, user.password)
        # Verificar que es un hash válido de Django
        self.assertTrue(check_password(raw_password, user.password))
        self.assertTrue(user.password.startswith('pbkdf2_') or user.password.startswith('argon2') or user.password.startswith('bcrypt'))

    def test_15_registro_exitoso_y_redireccion(self):
        """TEST 15: Registro exitoso redirige correctamente al inicio."""
        response = self.client.post(self.url, self.valid_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('index'))
        self.assertContains(response, 'usuario_nuevo')

    def test_16_post_redirect_get_evita_duplicacion(self):
        """TEST 16: Recargar la página tras el registro no vuelve a crear el usuario (Post/Redirect/Get)."""
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 302)
        initial_count = User.objects.count()

        # Simular GET a la URL de redirección (index) tras refrescar
        get_response = self.client.get(reverse('index'))
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(User.objects.count(), initial_count)
