import pytest
from rest_framework.test import APIClient
from unittest.mock import patch
from django.utils import timezone

from scanned_text.models import ScannedText
from account.models import User
from rest_framework.authtoken.models import Token


def create_user_with_token():
    user = User.objects.create(
        username=f"test_{timezone.now().timestamp()}",
        name="Test User",
        age=12,
        is_active=True,
    )
    token, _ = Token.objects.get_or_create(user=user)
    return user, token.key


@pytest.mark.django_db
class TestScannedTextAPI:
    def setup_method(self):
        self.client = APIClient()
        self.base_url = "/api/v1/scanned-texts/"
        import os
        os.environ["ENV"] = "testing"
        user, token = create_user_with_token()
        self.user = user
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    @patch("scanned_text.helpers.ai_utils.mock_detect_type")
    @patch("scanned_text.helpers.ai_utils.mock_process_text")
    def test_create_scanned_text(self, mock_process_text, mock_detect_type):
        mock_process_text.return_value = "Texte traité"
        mock_detect_type.return_value = "resume"
        data = {"original_text": "Ceci est un résumé du chapitre 1"}
        response = self.client.post(self.base_url, data, format="json")
        assert response.status_code == 201
        assert response.data["processed_text"] == "Texte traité"
        assert response.data["detected_type"] == "resume"
        created_id = response.data["id"]
        assert ScannedText.objects.filter(id=created_id).exists()

    def test_create_scanned_text_empty(self):
        response = self.client.post(self.base_url, {"original_text": "   "}, format="json")
        assert response.status_code == 400
        assert "error" in response.data

    @patch("scanned_text.helpers.ai.get_difficult_words_with_meanings.get_difficult_words_with_meanings")
    def test_difficult_words_basic(self, mock_words):
        mock_words.return_value = {"3": "Définition simple", "7": "Explication facile"}
        st = ScannedText.objects.create(
            user=self.user,
            original_text="Texte original",
            processed_text="Texte traité pour analyse",
            detected_type="cours",
        )
        url = f"{self.base_url}{st.id}/words-explanation/"
        resp = self.client.get(url)
        assert resp.status_code == 200
        assert resp.data["words"] == {"3": "Définition simple", "7": "Explication facile"}

    @patch("scanned_text.helpers.ai.get_difficult_words_with_meanings.get_difficult_words_with_meanings")
    def test_difficult_words_other_mapping(self, mock_words):
        mock_words.return_value = {"2": "Terme difficile"}
        st = ScannedText.objects.create(
            user=self.user,
            original_text="Autre texte",
            processed_text="Autre texte traité",
            detected_type="cours",
        )
        url = f"{self.base_url}{st.id}/words-explanation/"
        resp = self.client.get(url)
        assert resp.status_code == 200
        assert resp.data["words"] == {"2": "Terme difficile"}

    def test_difficult_words_missing_processed_text(self):
        st = ScannedText.objects.create(
            user=self.user,
            original_text="Sans processed",
            processed_text=None,
            detected_type="inconnu",
        )
        url = f"{self.base_url}{st.id}/words-explanation/"
        resp = self.client.get(url)
        assert resp.status_code == 400

    def test_difficult_words_not_found(self):
        import uuid
        missing_id = uuid.uuid4()
        url = f"{self.base_url}{missing_id}/words-explanation/"
        resp = self.client.get(url)
        assert resp.status_code == 404
