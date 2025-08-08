from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
import secrets

from .models import Doctor, Patient, AccessLog, TemporaryAccessToken
from .blockchain import request_access_on_chain, register_doctor_on_chain

# ------------------ Home ------------------
def home(request):
    return redirect('register_doctor')

# ------------------ Doctor Registration ------------------
# ------------------ Doctor Registration ------------------
def register_doctor(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        wallet = request.POST.get('wallet', '').strip()
        credit_str = request.POST.get('credit', '').strip()

        if not (name and wallet and credit_str):
            messages.error(request, "❌ All fields are required.")
            return redirect('register_doctor')

        if Doctor.objects.filter(wallet_address=wallet).exists():
            messages.error(request, "❌ Doctor already registered.")
            return redirect('register_doctor')

        try:
            credit = int(credit_str)
        except ValueError:
            messages.error(request, "❌ Credit level must be a number.")
            return redirect('register_doctor')

        try:
            tx_hash = register_doctor_on_chain(wallet, name, credit)
            doctor = Doctor.objects.create(name=name, wallet_address=wallet, credit_level=credit)

            # 🔑 set session to the NEW doctor
            request.session['doctor_id'] = doctor.id
            request.session['doctor_name'] = doctor.name
            request.session['wallet_address'] = doctor.wallet_address
            request.session['credit_level'] = doctor.credit_level

            messages.success(request, f"✅ Doctor registered successfully! TX: {tx_hash}")
            return redirect('doctor_dashboard')  # go straight to dashboard
        except Exception as e:
            messages.error(request, f"❌ {e}")
            return redirect('register_doctor')

    return render(request, 'register_doctor.html')



# ------------------ Doctor Login ------------------
def doctor_login(request):
    if request.method == "POST":
        wallet = request.POST.get("wallet", "").strip()
        try:
            doctor = Doctor.objects.get(wallet_address=wallet)
            request.session['doctor_id'] = doctor.id
            request.session['doctor_name'] = doctor.name
            request.session['wallet_address'] = doctor.wallet_address
            request.session['credit_level'] = doctor.credit_level   # add this
            messages.success(request, f"✅ Welcome, Dr. {doctor.name}!")
            return redirect("doctor_dashboard")
        except Doctor.DoesNotExist:
            messages.error(request, "❌ Wallet not registered.")
            return redirect("doctor_login")
    return render(request, "doctor_login.html")


# ------------------ Doctor Dashboard ------------------
def doctor_dashboard(request):
    doctor_name = request.session.get("doctor_name", "Doctor")
    patients = Patient.objects.all()[:10]
    return render(request, 'doctor_dashboard.html', {
        'doctor_name': doctor_name,
        'patients': patients
    })

# ------------------ Request Access (POST only, patient_id in form) ------------------

def request_access(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    patient_id = request.POST.get("patient_id")
    if not patient_id:
        return HttpResponseBadRequest("Missing patient_id")

    wallet = request.session.get("wallet_address")
    if not wallet:
        messages.error(request, "Please log in again.")
        return redirect("doctor_login")

    # Optional: on-chain check here

    # ensure patient exists (for safety)
    get_object_or_404(Patient, synthea_id=patient_id)

    token = secrets.token_urlsafe(16)
    expires_at = timezone.now() + timedelta(minutes=5)

    TemporaryAccessToken.objects.create(
        token=token,
        patient_id=patient_id,   # <-- matches your model
        expires_at=expires_at    # <-- matches your model
    )

    return redirect("view_patient", token=token)

# ------------------ View Patient Report ------------------
def view_patient(request, token):
    tok = get_object_or_404(TemporaryAccessToken, token=token)
    if tok.expires_at <= timezone.now():
        return render(request, "expired.html")

    seconds_left = int((tok.expires_at - timezone.now()).total_seconds())

    # pass the Patient model instance (not a dict)
    patient = get_object_or_404(Patient, synthea_id=tok.patient_id)

    return render(request, "view_patient.html", {
        "patient": patient,
        "seconds_left": seconds_left,
    })

# ------------------ Separate submit endpoint (kept if you need it) ------------------
def submit_register(request):
    if request.method != 'POST':
        return redirect('register_doctor')

    name = request.POST.get('name', '').strip()
    wallet = request.POST.get('wallet', '').strip()
    credit_str = request.POST.get('credit', '').strip()

    if not (name and wallet and credit_str):
        messages.error(request, '❌ All fields are required.')
        return redirect('register_doctor')

    if Doctor.objects.filter(wallet_address=wallet).exists():
        messages.error(request, '❌ Wallet already registered.')
        return redirect('register_doctor')

    try:
        credit = int(credit_str)
    except ValueError:
        messages.error(request, '❌ Credit level must be a number.')
        return redirect('register_doctor')

    try:
        tx_hash = register_doctor_on_chain(wallet, name, credit)
        doctor = Doctor.objects.create(name=name, wallet_address=wallet, credit_level=credit)

        # 🔑 set session to the NEW doctor
        request.session['doctor_id'] = doctor.id
        request.session['doctor_name'] = doctor.name
        request.session['wallet_address'] = doctor.wallet_address
        request.session['credit_level'] = doctor.credit_level

        messages.success(request, f"✅ Doctor registered successfully! TX: {tx_hash}")
        return redirect('doctor_dashboard')
    except Exception as e:
        messages.error(request, f"❌ Blockchain error: {e}")
        return redirect('register_doctor')

