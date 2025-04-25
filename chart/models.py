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
    is_admin = models.BooleanField(default=False)  # opcional

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    def __str__(self):
        return self.email

class Colaborador(models.Model):
    imagem = models.TextField(blank=True, null=True)
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.TextField(max_length=12)
    supervisor = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
