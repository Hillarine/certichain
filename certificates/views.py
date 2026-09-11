import qrcode
import io
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from .models import Certificate
from .forms import CertificateCreateForm, CertificateVerifyForm, CertificateRevokeForm
from .blockchain import get_blockchain_service


def home(request):
    """Page d'accueil"""
    total_certs = Certificate.objects.count()
    verified_certs = Certificate.objects.filter(status='registered').count()
    revoked_certs = Certificate.objects.filter(status='revoked').count()

    context = {
        'total_certs': total_certs,
        'verified_certs': verified_certs,
        'revoked_certs': revoked_certs,
    }
    return render(request, 'certificates/home.html', context)


def dashboard(request):
    """Dashboard principal"""
    certificates = Certificate.objects.all()

    # Statistiques
    total = certificates.count()
    registered = certificates.filter(status='registered').count()
    pending = certificates.filter(status='pending').count()
    revoked = certificates.filter(status='revoked').count()

    # Blockchain status
    blockchain = get_blockchain_service()
    blockchain_connected = blockchain.is_connected

    # Certificats récents
    recent_certificates = certificates[:10]

    context = {
        'certificates': recent_certificates,
        'total': total,
        'registered': registered,
        'pending': pending,
        'revoked': revoked,
        'blockchain_connected': blockchain_connected,
    }
    return render(request, 'certificates/dashboard.html', context)


def create_certificate(request):
    """Créer un nouveau certificat"""
    if request.method == 'POST':
        form = CertificateCreateForm(request.POST)
        if form.is_valid():
            certificate = form.save()

            # Tenter l'enregistrement blockchain
            blockchain = get_blockchain_service()
            if blockchain.is_connected and blockchain.contract:
                try:
                    result = blockchain.issue_certificate(
                        cert_id=certificate.certificate_id,
                        cert_hash=certificate.certificate_hash,
                        recipient_name=certificate.recipient_name,
                        title=certificate.title,
                        issuer_name=certificate.issuer_name,
                    )

                    certificate.tx_hash = result['tx_hash']
                    certificate.block_number = result['block_number']
                    certificate.issuer_wallet = result.get('from', '')
                    certificate.status = 'registered'
                    certificate.save()

                    messages.success(
                        request,
                        f'Certificat {certificate.certificate_id} créé et enregistré sur la blockchain !'
                    )
                except Exception as e:
                    certificate.status = 'failed'
                    certificate.save()
                    messages.warning(
                        request,
                        f'Certificat créé mais erreur blockchain : {str(e)}'
                    )
            else:
                messages.info(
                    request,
                    f'Certificat {certificate.certificate_id} créé (blockchain non disponible - mode hors-ligne).'
                )

            return redirect('certificate_detail', pk=certificate.pk)
    else:
        form = CertificateCreateForm()

    return render(request, 'certificates/create.html', {'form': form})


def certificate_detail(request, pk):
    """Détail d'un certificat"""
    certificate = get_object_or_404(Certificate, pk=pk)

    # Générer le QR code
    qr_data = request.build_absolute_uri(f'/verify/result/{certificate.certificate_id}/')
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#1a56db", back_color="white")

    buffer = io.BytesIO()
    qr_img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    # Vérification blockchain
    blockchain_data = None
    blockchain = get_blockchain_service()
    if blockchain.is_connected and blockchain.contract and certificate.status == 'registered':
        try:
            blockchain_data = blockchain.verify_certificate(certificate.certificate_id)
        except Exception:
            pass

    context = {
        'certificate': certificate,
        'qr_code': qr_base64,
        'blockchain_data': blockchain_data,
    }
    return render(request, 'certificates/detail.html', context)


def verify_certificate(request):
    """Page de vérification d'un certificat"""
    form = CertificateVerifyForm()

    if request.method == 'POST':
        form = CertificateVerifyForm(request.POST)
        if form.is_valid():
            certificate_id = form.cleaned_data['certificate_id'].strip()
            return redirect('verification_result', certificate_id=certificate_id)

    return render(request, 'certificates/verify.html', {'form': form})


def verification_result(request, certificate_id):
    """Résultat de la vérification"""
    certificate = Certificate.objects.filter(certificate_id=certificate_id).first()

    blockchain_verified = False
    blockchain_data = None
    blockchain_error = None

    if certificate:
        blockchain = get_blockchain_service()
        if blockchain.is_connected and blockchain.contract:
            try:
                blockchain_data = blockchain.verify_certificate(certificate_id)
                if blockchain_data.get('exists'):
                    blockchain_verified = True
            except Exception as e:
                blockchain_error = str(e)

    context = {
        'certificate_id': certificate_id,
        'certificate': certificate,
        'blockchain_verified': blockchain_verified,
        'blockchain_data': blockchain_data,
        'blockchain_error': blockchain_error,
    }
    return render(request, 'certificates/verification_result.html', context)


def revoke_certificate(request, pk):
    """Révoquer un certificat"""
    certificate = get_object_or_404(Certificate, pk=pk)

    if certificate.status == 'revoked':
        messages.error(request, 'Ce certificat est déjà révoqué.')
        return redirect('certificate_detail', pk=pk)

    if request.method == 'POST':
        form = CertificateRevokeForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']

            # Révoquer sur la blockchain
            blockchain = get_blockchain_service()
            if blockchain.is_connected and blockchain.contract and certificate.status == 'registered':
                try:
                    result = blockchain.revoke_certificate(certificate.certificate_id, reason)
                    certificate.revocation_tx_hash = result['tx_hash']
                except Exception as e:
                    messages.warning(request, f'Erreur blockchain lors de la révocation : {str(e)}')

            certificate.status = 'revoked'
            certificate.revocation_reason = reason
            certificate.revoked_at = timezone.now()
            certificate.save()

            messages.success(request, f'Certificat {certificate.certificate_id} révoqué avec succès.')
            return redirect('certificate_detail', pk=pk)
    else:
        form = CertificateRevokeForm()

    context = {
        'certificate': certificate,
        'form': form,
    }
    return render(request, 'certificates/revoke.html', context)


def api_blockchain_status(request):
    """API endpoint pour le statut blockchain"""
    blockchain = get_blockchain_service()
    return JsonResponse({
        'connected': blockchain.is_connected,
        'contract_configured': bool(blockchain.contract),
    })