from django.db import models
from django.contrib.auth.models import User

class ProfiloUtente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    failed_attempts = models.IntegerField(default=0)
    blocked_until = models.FloatField(default=0)
    firma_ascii = models.TextField(blank=True, default='')

    def __str__(self):
        return self.user.username

class Documentazione(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    titolo = models.CharField(max_length=200)
    contenuto = models.TextField()
    creata_il = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titolo