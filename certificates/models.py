import uuid
import hashlib
from django.db import models
from django.utils import timezone


class Certificate(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('registered', 'Enregistré'),
        ('revoked', 'Révoqué'),
        ('failed', 'Échoué'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certificate_id = models.CharField(max_length=20, unique=True, blank=True)

    # Informations du certificat
    recipient_name = models.CharField(max_length=255, verbose_name="Nom du destinataire")
    recipient_email = models.EmailField(verbose_name="Email du destinataire", blank=True)
    title = models.CharField(max_length=255, verbose_name="Titre du certificat")
    description = models.TextField(verbose_name="Description", blank=True)
    issuer_name = models.CharField(max_length=255, verbose_name="Organisme émetteur")
    issue_date = models.DateField(verbose_name="Date d'émission", default=timezone.now)
    expiry_date = models.DateField(verbose_name="Date d'expiration", null=True, blank=True)

    # Blockchain
    certificate_hash = models.CharField(max_length=66, blank=True)
    tx_hash = models.CharField(max_length=66, blank=True, verbose_name="Hash de transaction")
    block_number = models.IntegerField(null=True, blank=True)
    issuer_wallet = models.CharField(max_length=42, blank=True, verbose_name="Wallet émetteur")

    # Statut
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    revocation_reason = models.TextField(blank=True, verbose_name="Raison de révocation")
    revoked_at = models.DateTimeField(null=True, blank=True)
    revocation_tx_hash = models.CharField(max_length=66, blank=True)

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Certificat"
        verbose_name_plural = "Certificats"

    def __str__(self):
        return f"{self.certificate_id} - {self.title} ({self.recipient_name})"

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = self.generate_certificate_id()
        if not self.certificate_hash:
            self.certificate_hash = self.compute_hash()
        super().save(*args, **kwargs)

    def generate_certificate_id(self):
        timestamp = timezone.now().strftime('%y%m')
        random_part = uuid.uuid4().hex[:6].upper()
        return f"CERT-{timestamp}-{random_part}"

    def compute_hash(self):
        data = f"{self.certificate_id}{self.recipient_name}{self.title}{self.issuer_name}{self.issue_date}"
        return '0x' + hashlib.sha256(data.encode()).hexdigest()

    @property
    def is_valid(self):
        if self.status == 'revoked':
            return False
        if self.expiry_date and self.expiry_date < timezone.now().date():
            return False
        return self.status == 'registered'

    @property
    def status_display_class(self):
        classes = {
            'pending': 'warning',
            'registered': 'success',
            'revoked': 'danger',
            'failed': 'danger',
        }
        return classes.get(self.status, 'secondary')