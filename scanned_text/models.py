from django.db import models
import uuid

from account.models import User


class ScannedText(models.Model):
    RAW_TYPES = [
        ('exercice', 'Exercice'),
        ('texte', 'Texte'),
        ('inconnu', 'Inconnu'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scanned_texts')
    original_text = models.TextField()
    processed_text = models.TextField(blank=True, null=True)
    detected_type = models.CharField(max_length=20, choices=RAW_TYPES, default='inconnu')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Texte scanné #{self.id} ({self.detected_type})"
