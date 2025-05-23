from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, nome, password, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório')
        if not password:
            raise ValueError('A senha é obrigatória')
        
        email = self.normalize_email(email)
        user = self.model(email=email, nome=nome, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, nome, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    def __str__(self):
        return self.email

class Colaborador(models.Model):
    imagem = models.ImageField(blank=True, null=True, default='user.png', upload_to='profile_pics')
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.TextField(max_length=12)
    supervisor = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    cargo = models.ForeignKey("Cargo", on_delete=models.SET_DEFAULT, default=None)

    def __str__(self):
        return self.nome

class Cargo(models.Model):
    nome = models.CharField(max_length=100)
    salario = models.FloatField(blank=True, default=0)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nome

