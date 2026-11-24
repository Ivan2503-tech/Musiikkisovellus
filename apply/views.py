from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import Cancion, Playlist, PlaylistCancion, Favorito, Perfil, HistorialReproduccion
from django.http import JsonResponse
from django.db.models import Count
from django.contrib.auth import update_session_auth_hash
from .models import Cancion
from django.templatetags.static import static
from django.urls import reverse
from urllib.parse import urlencode


canciones = {
    "find-your-flame": {
        "nombre": "Find Your Flame",
        "artista": "SEGA SOUND TEAM • Kellin Quinn • Tyler Smyth",
        "imagen": "apply/img/Sonic_Frontiers.jpg",
        "audio": "/media/audio/Find Your Flame.mp3",
    },
    "break-through-it-all": {
        "nombre": "Break Through It All",
        "artista": "SEGA SOUND TEAM  • Kellin Quinn",
        "imagen": "apply/img/Sonic_Frontiers.jpg",
        "audio": "/media/audio/break_through_it_all.mp3",
    },
    "breaking-the-habit": {
        "nombre": "Breaking the Habit",
        "artista": "Linkin Park",
        "imagen": "apply/img/Linkin_Park.jpg",
        "audio": "/media/audio/breaking_the_habit.mp3",
    },
    "bring-me-to-life": {
        "nombre": "Bring Me To Life",
        "artista": "Evanescence",
        "imagen": "apply/img/Evanescence.jpg",
        "audio": "/media/audio/bring_me_to_life.mp3",
    },
    "bodies": {
        "nombre": "Bodies",
        "artista": "Drowning Pool",
        "imagen": "apply/img/Drowning_Pool.jpg",
        "audio": "/media/audio/Bodies.mp3",
    },
    "colors-flying-high": {
        "nombre": "Colors Flying High",
        "artista": "Persona 5",
        "imagen": "apply/img/Persona_5.jpg",
        "audio": "/media/audio/Colors Flying High.mp3",
    },
    "come-alive": {
        "nombre": "Come Alive",
        "artista": "Sān-Z",
        "imagen": "apply/img/come_alive.jpg",
        "audio": "/media/audio/Come Alive.mp3",
    },
    "dare": {
        "nombre": "Dare",
        "artista": "Gorillaz",
        "imagen": "apply/img/Gorillaz.jpg",
        "audio": "/media/audio/DARE.mp3",
    },
    "Lions": {
        "nombre": "Lions",
        "artista": "Skillet",
        "imagen": "apply/img/Unleashed.jpg",
        "audio": "/media/audio/Lions.mp3",
    },
    "Feel-Invincible": {
        "nombre": "Feel Invincible",
        "artista": "Skillet",
        "imagen": "apply/img/Unleashed.jpg",
        "audio": "/media/audio/Feel Invincible.mp3",
    },
    "Afterlife": {
        "nombre": "Afterlife",
        "artista": "Evanescence",
        "imagen": "apply/img/DMC_afterlife.jpg",
        "audio": "/media/audio/Afterlife.mp3",
    },
    "Heaven": {
        "nombre": "Heaven",
        "artista": "Atlus • Shihoko Hirata",
        "imagen": "apply/img/Golden.jpg",
        "audio": "/media/audio/Heaven.mp3",
    },
    "ColorYourNight": {
        "nombre": "Color Your Night",
        "artista": "Atlus • Azumi Takahashi • Lotus Juice",
        "imagen": "apply/img/Reload.jpg",
        "audio": "/media/audio/ColorYourNight.mp3",
    },
    "A-Little-Faster": {
        "nombre": "A Little Faster",
        "artista": "There For Tomorrow",
        "imagen": "apply/img/There.jpg",
        "audio": "/media/audio/A Little Faster.mp3",
    },
}


def es_administrador(user):
    return user.is_authenticated and user.is_staff
def activar_administrador(username):
    usuario = User.objects.get(username=username)
    usuario.is_staff = True
    usuario.is_superuser = True
    usuario.save()
    return usuario


def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect("inicio")

    if request.method == "POST":
        correo = request.POST.get("Correo", "").strip()
        password = request.POST.get("Contraseña", "")

        usuario = User.objects.filter(email__iexact=correo).first()

        if usuario:
            usuario = authenticate(
                request,
                username=usuario.username,
                password=password
            )

        if usuario is not None:
            login(request, usuario)
            return redirect("inicio")

        return render(request, "login.html", {
            "error": "Correo electrónico o contraseña incorrectos"
        })

    return render(request, "login.html")


def registrar(request):
    if request.user.is_authenticated:
        return redirect("inicio")

    if request.method == "POST":
        username = request.POST.get("Usuario", "").strip()
        email = request.POST.get("Correo", "").strip()
        password = request.POST.get("Contraseña", "")
        password2 = request.POST.get("ConfirmarContraseña", "")

        if not username or not email or not password:
            return render(request, "registro.html", {
                "error": "Todos los campos son obligatorios"
            })

        if password != password2:
            return render(request, "registro.html", {
                "error": "Las contraseñas no coinciden"
            })

        if User.objects.filter(username__iexact=username).exists():
            return render(request, "registro.html", {
                "error": "Ese nombre de usuario ya existe"
            })

        if User.objects.filter(email__iexact=email).exists():
            return render(request, "registro.html", {
                "error": "Ese correo ya está registrado"
            })

        try:
            validate_password(password)
        except ValidationError as error:
            return render(request, "registro.html", {
                "error": " ".join(error.messages)
            })

        usuario = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, usuario)
        return redirect("inicio")

    return render(request, "registro.html")



@login_required
def inicio(request):
    canciones_db = Cancion.objects.all()
    playlists = Playlist.objects.filter(usuario=request.user)

    return render(request, "index.html", {
        "canciones_db": canciones_db,
        "playlists": playlists
    })

@login_required
def reproductor(request, slug):
    datos = obtener_datos_cancion(slug)

    origen = request.GET.get("origen", "biblioteca")
    playlist_id = request.GET.get("playlist_id")

    if origen == "favoritos":
        favoritos = Favorito.objects.filter(
            usuario=request.user
        )

        lista = []

        for favorito in favoritos:
            try:
                lista.append(
                    obtener_datos_cancion(favorito.slug_cancion)
                )
            except Exception:
                continue

    elif origen == "playlist" and playlist_id:
        playlist = get_object_or_404(
            Playlist,
            id=playlist_id,
            usuario=request.user
        )

        lista = []

        for elemento in playlist.canciones.all():
            try:
                lista.append(
                    obtener_datos_cancion(elemento.slug_cancion)
                )
            except Exception:
                continue

    else:
        origen = "biblioteca"
        playlist_id = None
        lista = obtener_biblioteca()

    if not any(c["slug"] == slug for c in lista):
        lista.append(datos)

    cola = preparar_cola(lista, origen, playlist_id)

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "favorito":
            favorito = Favorito.objects.filter(
                usuario=request.user,
                slug_cancion=slug
            ).first()

            if favorito:
                favorito.delete()
                es_favorita = False
            else:
                Favorito.objects.get_or_create(
                    usuario=request.user,
                    slug_cancion=slug
                )
                es_favorita = True

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "success": True,
                    "es_favorita": es_favorita
                })

            messages.success(
                request,
                "Favorito actualizado correctamente."
            )

        elif accion == "playlist":
            playlist_id_post = request.POST.get("playlist_id")

            playlist = get_object_or_404(
                Playlist,
                id=playlist_id_post,
                usuario=request.user
            )

            PlaylistCancion.objects.get_or_create(
                playlist=playlist,
                slug_cancion=slug
            )

            messages.success(
                request,
                f"Canción agregada a {playlist.nombre}."
            )

        return redirect(
            reverse("reproductor", kwargs={"slug": slug})
            + "?"
            + urlencode({
                "origen": origen,
                **({"playlist_id": playlist_id} if playlist_id else {})
            })
        )

    es_favorita = Favorito.objects.filter(
        usuario=request.user,
        slug_cancion=slug
    ).exists()

    playlists = Playlist.objects.filter(
        usuario=request.user
    )

    return render(request, "reproductor.html", {
        "cancion": datos,
        "imagen_estatica": datos["imagen_estatica"],
        "es_favorita": es_favorita,
        "playlists": playlists,
        "cola_reproduccion": cola,
        "origen_reproduccion": origen,
        "playlist_id": playlist_id
    })


def cerrar_sesion(request):
    if request.method != "POST":
        return redirect("inicio")

    logout(request)
    return redirect("login")


@user_passes_test(es_administrador, login_url="inicio")
def cuentas(request):
    usuarios = User.objects.all().order_by("id")

    return render(request, "cuentas.html", {
        "usuarios": usuarios
    })


@user_passes_test(es_administrador, login_url="inicio")
def crear_cuenta(request):
    if request.method == "POST":
        username = request.POST.get("Usuario", "").strip()
        email = request.POST.get("Correo", "").strip()
        password = request.POST.get("Contraseña", "")
        password2 = request.POST.get("ConfirmarContraseña", "")

        if not username or not email or not password:
            return render(request, "cuenta_form.html", {
                "titulo": "Crear cuenta",
                "error": "Todos los campos son obligatorios"
            })

        if User.objects.filter(username__iexact=username).exists():
            return render(request, "cuenta_form.html", {
                "titulo": "Crear cuenta",
                "error": "Ese usuario ya existe"
            })

        if User.objects.filter(email__iexact=email).exists():
            return render(request, "cuenta_form.html", {
                "titulo": "Crear cuenta",
                "error": "Ese correo ya está registrado"
            })

        if password != password2:
            return render(request, "cuenta_form.html", {
                "titulo": "Crear cuenta",
                "error": "Las contraseñas no coinciden"
            })

        try:
            validate_password(password)
        except ValidationError as error:
            return render(request, "cuenta_form.html", {
                "titulo": "Crear cuenta",
                "error": " ".join(error.messages)
            })

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect("cuentas")

    return render(request, "cuenta_form.html", {
        "titulo": "Crear cuenta"
    })


@user_passes_test(es_administrador, login_url="inicio")
def editar_cuenta(request, id):
    cuenta = get_object_or_404(User, pk=id)

    if cuenta.is_superuser:
        return redirect("cuentas")

    if request.method == "POST":
        username = request.POST.get("Usuario", "").strip()
        email = request.POST.get("Correo", "").strip()
        password = request.POST.get("Contraseña", "")

        if not username or not email:
            return render(request, "cuenta_form.html", {
                "titulo": "Editar cuenta",
                "cuenta": cuenta,
                "error": "Usuario y correo son obligatorios"
            })

        if User.objects.filter(
            username__iexact=username
        ).exclude(pk=cuenta.pk).exists():
            return render(request, "cuenta_form.html", {
                "titulo": "Editar cuenta",
                "cuenta": cuenta,
                "error": "Ese usuario ya existe"
            })

        if User.objects.filter(
            email__iexact=email
        ).exclude(pk=cuenta.pk).exists():
            return render(request, "cuenta_form.html", {
                "titulo": "Editar cuenta",
                "cuenta": cuenta,
                "error": "Ese correo ya está registrado"
            })

        if password:
            try:
                validate_password(password, user=cuenta)
            except ValidationError as error:
                return render(request, "cuenta_form.html", {
                    "titulo": "Editar cuenta",
                    "cuenta": cuenta,
                    "error": " ".join(error.messages)
                })

            cuenta.set_password(password)

        cuenta.username = username
        cuenta.email = email
        cuenta.save()

        return redirect("cuentas")

    return render(request, "cuenta_form.html", {
        "titulo": "Editar cuenta",
        "cuenta": cuenta
    })


@user_passes_test(es_administrador, login_url="inicio")
def eliminar_cuenta(request, id):
    cuenta = get_object_or_404(User, pk=id)

    if cuenta.is_superuser or cuenta.pk == request.user.pk:
        return redirect("cuentas")

    if request.method == "POST":
        cuenta.delete()
        return redirect("cuentas")

    return render(request, "cuenta_confirmar_eliminar.html", {
        "cuenta": cuenta
    })


@login_required
def mi_perfil(request):
    perfil, creado = Perfil.objects.get_or_create(usuario=request.user)
    favoritos = Favorito.objects.filter(usuario=request.user)
    canciones_favoritas = []
    for favorito in favoritos[:8]:
        try:
            canciones_favoritas.append(obtener_datos_cancion(favorito.slug_cancion))
        except Exception:
            continue
    mas_escuchadas = []
    reproducciones = HistorialReproduccion.objects.filter(usuario=request.user).values("slug_cancion").annotate(total=Count("id")).order_by("-total")[:8]
    for item in reproducciones:
        try:
            datos = obtener_datos_cancion(item["slug_cancion"])
            datos["total"] = item["total"]
            mas_escuchadas.append(datos)
        except Exception:
            continue
    playlists = Playlist.objects.filter(usuario=request.user)
    return render(request, "perfil.html", {
        "perfil": perfil,
        "canciones_favoritas": canciones_favoritas,
        "mas_escuchadas": mas_escuchadas,
        "playlists": playlists,
        "total_favoritos": favoritos.count(),
        "total_reproducciones": HistorialReproduccion.objects.filter(usuario=request.user).count(),
        "total_playlists": playlists.count(),
    })


@login_required
def editar_perfil(request):
    perfil, creado = Perfil.objects.get_or_create(usuario=request.user)
    if request.method == "POST":
        accion = request.POST.get("accion")
        usuario = request.user
        if accion == "personal":
            usuario.first_name = request.POST.get("Nombre", "").strip()
            usuario.last_name = request.POST.get("Apellido", "").strip()
            perfil.biografia = request.POST.get("biografia", "").strip()
            if len(perfil.biografia) > 300:
                return render(request, "editar_perfil.html", {"perfil": perfil, "seccion": "personal", "error": "La biografía no puede superar 300 caracteres."})
            usuario.save()
            perfil.save()
        elif accion == "foto":
            foto = request.FILES.get("foto")
            portada = request.FILES.get("portada")
            if foto:
                perfil.foto = foto
            if portada:
                perfil.portada = portada
            perfil.save()
        elif accion == "usuario":
            username = request.POST.get("Usuario", "").strip()
            if not username:
                return render(request, "editar_perfil.html", {"perfil": perfil, "seccion": "usuario", "error": "El usuario es obligatorio."})
            if User.objects.filter(username__iexact=username).exclude(pk=usuario.pk).exists():
                return render(request, "editar_perfil.html", {"perfil": perfil, "seccion": "usuario", "error": "Ese nombre de usuario ya está ocupado."})
            usuario.username = username
            usuario.save()
        elif accion == "correo":
            correo = request.POST.get("Correo", "").strip()
            if not correo:
                return render(request, "editar_perfil.html", {"perfil": perfil, "seccion": "correo", "error": "El correo es obligatorio."})
            if User.objects.filter(email__iexact=correo).exclude(pk=usuario.pk).exists():
                return render(request, "editar_perfil.html", {"perfil": perfil, "seccion": "correo", "error": "Ese correo ya está registrado."})
            usuario.email = correo
            usuario.save()
        elif accion == "contrasena":
            actual = request.POST.get("actual", "")
            nueva = request.POST.get("nueva", "")
            confirmar = request.POST.get("confirmar", "")
            if not usuario.check_password(actual):
                return render(request, "editar_perfil.html", {"perfil": perfil, "seccion": "contrasena", "error": "La contraseña actual es incorrecta."})
            if nueva != confirmar:
                return render(request, "editar_perfil.html", {"perfil": perfil, "seccion": "contrasena", "error": "Las contraseñas nuevas no coinciden."})
            try:
                validate_password(nueva, user=usuario)
            except ValidationError as error:
                return render(request, "editar_perfil.html", {"perfil": perfil, "seccion": "contrasena", "error": " ".join(error.messages)})
            usuario.set_password(nueva)
            usuario.save()
            update_session_auth_hash(request, usuario)
        elif accion == "privacidad":
            perfil.mostrar_favoritos = request.POST.get("mostrar_favoritos") == "on"
            perfil.mostrar_mas_escuchadas = request.POST.get("mostrar_mas_escuchadas") == "on"
            perfil.mostrar_playlists = request.POST.get("mostrar_playlists") == "on"
            perfil.mostrar_actividad = request.POST.get("mostrar_actividad") == "on"
            perfil.mostrar_biografia = request.POST.get("mostrar_biografia") == "on"
            perfil.perfil_publico = request.POST.get("perfil_publico") == "on"
            perfil.save()
        messages.success(request, "Los cambios se guardaron correctamente.")
        return redirect("editar_perfil")
    seccion = request.GET.get("seccion", "personal")
    return render(request, "editar_perfil.html", {"perfil": perfil, "seccion": seccion})


@login_required
def registrar_reproduccion(request, slug):
    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)
    obtener_datos_cancion(slug)
    HistorialReproduccion.objects.create(usuario=request.user, slug_cancion=slug)
    return JsonResponse({"success": True})

@login_required
def eliminar_mi_cuenta(request):
    if request.method == "POST":
        usuario = request.user
        logout(request)
        usuario.delete()
        return redirect("login")

    return render(request, "eliminar_perfil.html")


@user_passes_test(es_administrador, login_url="inicio")
def administrar_musica(request):
    canciones_db = Cancion.objects.all()

    return render(request, "administrar_musica.html", {
        "canciones": canciones_db
    })


@user_passes_test(es_administrador, login_url="inicio")
def agregar_cancion(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        artista = request.POST.get("artista", "").strip()
        imagen = request.FILES.get("imagen")
        audio = request.FILES.get("audio")

        if not nombre or not artista or not imagen or not audio:
            return render(request, "cancion_form.html", {
                "titulo": "Agregar canción",
                "error": "Todos los campos son obligatorios"
            })

        Cancion.objects.create(
            nombre=nombre,
            artista=artista,
            imagen=imagen,
            audio=audio
        )

        messages.success(request, "¡Canción agregada correctamente!")

        return redirect("agregar_cancion")

    return render(request, "cancion_form.html", {
        "titulo": "Agregar canción"
    })

@user_passes_test(es_administrador, login_url="inicio")
def editar_cancion(request, id):
    cancion = get_object_or_404(Cancion, pk=id)

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        artista = request.POST.get("artista", "").strip()
        imagen = request.FILES.get("imagen")
        audio = request.FILES.get("audio")

        if not nombre or not artista:
            return render(request, "cancion_form.html", {
                "titulo": "Editar canción",
                "cancion": cancion,
                "error": "El nombre y el artista son obligatorios"
            })

        cancion.nombre = nombre
        cancion.artista = artista

        if imagen:
            cancion.imagen = imagen

        if audio:
            cancion.audio = audio

        cancion.save()

        return redirect("administrar_musica")

    return render(request, "cancion_form.html", {
        "titulo": "Editar canción",
        "cancion": cancion
    })


@user_passes_test(es_administrador, login_url="inicio")
def eliminar_cancion(request, id):
    cancion = get_object_or_404(Cancion, pk=id)

    if request.method == "POST":
        if cancion.imagen:
            cancion.imagen.delete(save=False)

        if cancion.audio:
            cancion.audio.delete(save=False)

        cancion.delete()

        return redirect("administrar_musica")

    return render(request, "cancion_confirmar_eliminar.html", {
        "cancion": cancion
    })

def obtener_datos_cancion(slug):
    cancion = canciones.get(slug)

    if cancion:
        return {
            "slug": slug,
            "nombre": cancion["nombre"],
            "artista": cancion["artista"],
            "imagen": cancion["imagen"],
            "audio": cancion["audio"],
            "imagen_estatica": True
        }

    cancion_db = get_object_or_404(Cancion, slug=slug)

    return {
        "slug": cancion_db.slug,
        "nombre": cancion_db.nombre,
        "artista": cancion_db.artista,
        "imagen": cancion_db.imagen.url,
        "audio": cancion_db.audio.url,
        "imagen_estatica": False
    }


@login_required
def crear_playlist(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()

        if not nombre:
            messages.error(request, "Escribe un nombre para la playlist.")
            return redirect("inicio")

        if Playlist.objects.filter(
            usuario=request.user,
            nombre__iexact=nombre
        ).exists():
            messages.error(request, "Ya tienes una playlist con ese nombre.")
            return redirect("inicio")

        Playlist.objects.create(
            usuario=request.user,
            nombre=nombre,
            descripcion=descripcion
        )

        messages.success(request, "Playlist creada correctamente.")
        return redirect("inicio")

    return redirect("inicio")


@login_required
def ver_playlist(request, id):
    playlist = get_object_or_404(
        Playlist,
        id=id,
        usuario=request.user
    )

    canciones_playlist = []

    for elemento in playlist.canciones.all():
        try:
            datos = obtener_datos_cancion(elemento.slug_cancion)
            canciones_playlist.append(datos)
        except Exception:
            continue

    return render(request, "playlist.html", {
        "playlist": playlist,
        "canciones_playlist": canciones_playlist
    })


@login_required
def eliminar_playlist(request, id):
    playlist = get_object_or_404(
        Playlist,
        id=id,
        usuario=request.user
    )

    if request.method == "POST":
        playlist.delete()
        messages.success(request, "Playlist eliminada.")
    
    return redirect("inicio")


@login_required
def quitar_cancion_playlist(request, id, slug):
    playlist = get_object_or_404(
        Playlist,
        id=id,
        usuario=request.user
    )

    if request.method == "POST":
        PlaylistCancion.objects.filter(
            playlist=playlist,
            slug_cancion=slug
        ).delete()

        messages.success(request, "Canción eliminada de la playlist.")

    return redirect("ver_playlist", id=playlist.id)


@login_required
def mis_favoritos(request):
    favoritos = Favorito.objects.filter(usuario=request.user)
    canciones_favoritas = []

    for favorito in favoritos:
        try:
            canciones_favoritas.append(
                obtener_datos_cancion(favorito.slug_cancion)
            )
        except Exception:
            continue

    return render(request, "favoritos.html", {
        "canciones_favoritas": canciones_favoritas
    })

def obtener_biblioteca():
    lista = []

    for slug in canciones:
        lista.append(obtener_datos_cancion(slug))

    for cancion_db in Cancion.objects.all():
        lista.append(obtener_datos_cancion(cancion_db.slug))

    return lista


def preparar_cola(lista, origen="biblioteca", playlist_id=None):
    cola = []

    for cancion in lista:
        datos = cancion.copy()

        if datos["imagen_estatica"]:
            datos["imagen_url"] = static(datos["imagen"])
        else:
            datos["imagen_url"] = datos["imagen"]

        parametros = {"origen": origen}

        if playlist_id:
            parametros["playlist_id"] = playlist_id

        datos["url"] = (
            reverse("reproductor", kwargs={"slug": datos["slug"]})
            + "?"
            + urlencode(parametros)
        )

        cola.append(datos)

    return cola