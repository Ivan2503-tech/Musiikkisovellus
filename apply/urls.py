from django.urls import path
from apply import views

urlpatterns = [
    path("", views.iniciar_sesion, name="login"),
    path("login/", views.iniciar_sesion, name="iniciar_sesion"),
    path("registro/", views.registrar, name="registro"),
    path("inicio/", views.inicio, name="inicio"),
    path("cancion/<slug:slug>/", views.reproductor, name="reproductor"),
    path("logout/", views.cerrar_sesion, name="logout"),

    path("cuentas/", views.cuentas, name="cuentas"),
    path("cuentas/crear/", views.crear_cuenta, name="crear_cuenta"),
    path("cuentas/editar/<int:id>/", views.editar_cuenta, name="editar_cuenta"),
    path("cuentas/eliminar/<int:id>/", views.eliminar_cuenta, name="eliminar_cuenta"),

    path("perfil/", views.mi_perfil, name="mi_perfil"),
    path("perfil/editar/", views.editar_perfil, name="editar_perfil"),
    path("perfil/reproducir/<slug:slug>/", views.registrar_reproduccion, name="registrar_reproduccion"),
    path("perfil/eliminar/", views.eliminar_mi_cuenta, name="eliminar_mi_cuenta"),

    path("musica/", views.administrar_musica, name="administrar_musica"),
    path("musica/agregar/", views.agregar_cancion, name="agregar_cancion"),
    path("musica/editar/<int:id>/", views.editar_cancion, name="editar_cancion"),
    path("musica/eliminar/<int:id>/", views.eliminar_cancion, name="eliminar_cancion"),

    path("playlists/crear/", views.crear_playlist, name="crear_playlist"),
    path("playlists/<int:id>/", views.ver_playlist, name="ver_playlist"),
    path("playlists/<int:id>/eliminar/", views.eliminar_playlist, name="eliminar_playlist"),
    path("playlists/<int:id>/quitar/<slug:slug>/", views.quitar_cancion_playlist, name="quitar_cancion_playlist"),
    path("audio/<str:nombre_archivo>", views.servir_audio, name="servir_audio"),

    path("favoritos/", views.mis_favoritos, name="mis_favoritos"),
]