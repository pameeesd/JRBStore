from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Categoria(models.Model):
    codigo = models.CharField(primary_key=True, max_length=60)
    categoria = models.CharField(max_length=50)
    subcategoria = models.CharField(max_length=50, default='General')

    def __str__(self):
        if self.subcategoria and self.subcategoria != 'General':
            return f"{self.categoria} - {self.subcategoria}"
        return f"{self.categoria}"

    class Meta:
        db_table = 'categoria'
        unique_together = ('categoria', 'subcategoria')


class Producto(models.Model):
    codigoBarra = models.CharField(primary_key=True, max_length=60)
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, null=False, on_delete=models.PROTECT)
    precio = models.DecimalField(max_digits=12, decimal_places=0)
    stock = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    descripcion = models.TextField(max_length=500)
    foto = models.ImageField(upload_to='productos')

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
        db_table = 'producto'


class Venta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venta {self.id} - {self.usuario.username}"


class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('PAGADO', 'Pagado'),
        ('RECHAZADO', 'Rechazado'),
        ('PENDIENTE', 'Pendiente'),
    ]

    numero_pedido = models.CharField(max_length=30, unique=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PAGADO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido {self.numero_pedido} - {self.usuario or 'Invitado'}"

    class Meta:
        db_table = 'pedido'


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
    codigo_barra_historico = models.CharField(max_length=60)
    nombre_producto_historico = models.CharField(max_length=100)
    precio_unitario_historico = models.DecimalField(max_digits=12, decimal_places=0)
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=0)

    def __str__(self):
        return f"{self.cantidad}x {self.nombre_producto_historico} ({self.pedido.numero_pedido})"

    class Meta:
        db_table = 'pedido_item'

