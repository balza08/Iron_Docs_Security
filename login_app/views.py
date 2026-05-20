from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from .models import Documentazione, ProfiloUtente

import io


# -------------------------
# AUTH / PAGINE
# -------------------------

def login_view(request):
    errore = None
    if request.method == "POST":
        username_input = request.POST.get("username")
        password_input = request.POST.get("password")
        
        # Controlla se l'utente esiste e la password è corretta
        user = authenticate(request, username=username_input, password=password_input)
        
        if user is not None:
            login(request, user)  # Crea la sessione
            return redirect("home")  # Vai alla home
        else:
            errore = "Credenziali non valide. Accesso negato."
            
    return render(request, "login.html", {"errore": errore})


def register_view(request):
    errore = None
    if request.method == "POST":
        username_input = request.POST.get("username")
        password_input = request.POST.get("password")
        firma_input = request.POST.get("firma_ascii", "") # Prende la firma dal form
        
        if User.objects.filter(username=username_input).exists():
            errore = "Questo username è già registrato nel sistema."
        else:
            # Crea l'utente criptando la password
            user = User.objects.create_user(username=username_input, password=password_input)
            
            # Salva la Firma ASCII nel tuo modello collegato
            ProfiloUtente.objects.create(user=user, firma_ascii=firma_input)
            
            login(request, user)  # Logga l'utente automaticamente
            return redirect("home")

    return render(request, "register.html", {"errore": errore})


def logout_view(request):
    logout(request)  # Cancella i cookie di sessione dal browser fondamentale!!
    return redirect("login")


# -------------------------
# HOME
# -------------------------

def home(request):
    if request.user.is_authenticated:
        docs = Documentazione.objects.filter(user=request.user)
    else:
        docs = []

    return render(request, "home.html", {"docs": docs})


# -------------------------
# DOCUMENTI
# -------------------------

@login_required
def nuova_doc(request):
    return render(request, "nuova_doc.html")


@login_required
def visualizza_doc(request, doc_id):
    doc = get_object_or_404(Documentazione, id=doc_id, user=request.user)
    return render(request, "visualizza_doc.html", {"doc": doc})


@login_required
def elimina_doc(request, doc_id):
    doc = get_object_or_404(Documentazione, id=doc_id, user=request.user)
    doc.delete()
    return redirect("home")


# -------------------------
# DOWNLOAD TXT
# -------------------------

@login_required
def scarica_txt(request, doc_id):

    doc = get_object_or_404(Documentazione, id=doc_id, user=request.user)
    profilo, _ = ProfiloUtente.objects.get_or_create(user=request.user)

    contenuto = f"{profilo.firma_ascii}\n\n"
    contenuto += f"TITOLO: {doc.titolo}\n"
    contenuto += f"DATA: {doc.creata_il.strftime('%d/%m/%Y %H:%M')}\n"
    contenuto += f"AUTORE: {request.user.username}\n"
    contenuto += "-" * 80 + "\n\n"
    contenuto += doc.contenuto

    response = HttpResponse(contenuto, content_type="text/plain")
    response["Content-Disposition"] = f'attachment; filename="{doc.titolo}.txt"'
    return response


# -------------------------
# DOWNLOAD PDF
# -------------------------

@login_required
def scarica_pdf(request, doc_id):

    doc = get_object_or_404(Documentazione, id=doc_id, user=request.user)
    profilo, _ = ProfiloUtente.objects.get_or_create(user=request.user)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4

    # sfondo
    p.setFillColorRGB(0.04, 0.04, 0.04)
    p.rect(0, 0, width, height, fill=1)

    p.setFillColorRGB(0, 1, 0.25)
    p.setFont("Courier", 9)

    y = height - 40

    # firma
    for riga in profilo.firma_ascii.split("\n"):
        p.drawString(30, y, riga[:100])
        y -= 12

    y -= 20

    # titolo
    p.setFont("Courier-Bold", 12)
    p.drawString(30, y, doc.titolo)

    y -= 20

    # contenuto
    p.setFont("Courier", 9)

    for riga in doc.contenuto.split("\n"):
        if y < 40:
            p.showPage()
            p.setFillColorRGB(0.04, 0.04, 0.04)
            p.rect(0, 0, width, height, fill=1)
            p.setFillColorRGB(0, 1, 0.25)
            p.setFont("Courier", 9)
            y = height - 40

        p.drawString(30, y, riga[:100])
        y -= 14

    p.save()
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="application/pdf")