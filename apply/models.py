from django.db import models
from django.conf import settings
from django.utils.text import slugify


class ejemplo(models.Model):
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    edad = models.IntegerField()
    carrera = models.CharField(max_length=150)


class Cancion(models.Model):
    nombre = models.CharField(max_length=200)
    artista = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, blank=True)
    imagen = models.ImageField(upload_to="portadas/")
    audio = models.FileField(upload_to="audio/")
    fecha_agregada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.nombre)
            slug = base
            contador = 1
            while Cancion.objects.filter(slug=slug).exists():
                slug = f"{base}-{contador}"
                contador += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} - {self.artista}"


class Playlist(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="playlists")
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=250, blank=True)
    imagen = models.ImageField(upload_to="playlists/", blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_creacion"]
        constraints = [models.UniqueConstraint(fields=["usuario", "nombre"], name="playlist_nombre_por_usuario")]

    def __str__(self):
        return self.nombre


class PlaylistCancion(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name="canciones")
    slug_cancion = models.CharField(max_length=200)
    fecha_agregada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fecha_agregada"]
        constraints = [models.UniqueConstraint(fields=["playlist", "slug_cancion"], name="cancion_unica_por_playlist")]

    def __str__(self):
        return f"{self.playlist.nombre} - {self.slug_cancion}"


class Favorito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favoritos")
    slug_cancion = models.CharField(max_length=200)
    fecha_agregada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_agregada"]
        constraints = [models.UniqueConstraint(fields=["usuario", "slug_cancion"], name="favorito_unico_por_usuario")]

    def __str__(self):
        return f"{self.usuario.username} - {self.slug_cancion}"


class Perfil(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil")
    foto = models.ImageField(upload_to="perfiles/", blank=True, null=True)
    portada = models.ImageField(upload_to="portadas_perfil/", blank=True, null=True)
    biografia = models.CharField(max_length=300, blank=True)
    mostrar_favoritos = models.BooleanField(default=True)
    mostrar_mas_escuchadas = models.BooleanField(default=True)
    mostrar_playlists = models.BooleanField(default=True)
    mostrar_actividad = models.BooleanField(default=False)
    mostrar_biografia = models.BooleanField(default=True)
    perfil_publico = models.BooleanField(default=True)

    def __str__(self):
        return f"Perfil de {self.usuario.username}"


class HistorialReproduccion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="historial_musical")
    slug_cancion = models.CharField(max_length=200)
    fecha_reproduccion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_reproduccion"]

    def __str__(self):
        return f"{self.usuario.username} - {self.slug_cancion}"
