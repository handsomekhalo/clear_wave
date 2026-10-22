
# system_management/tests/case_documents_test.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
import uuid

from document_management.models import Document, DocumentAccess
from system_management.models import User, Firm
from case_management.models import Case, CaseType

from .test_case_management import BaseCaseTest  # import your base if separate


class DocumentTests(BaseCaseTest):
    def setUp(self):
        super().setUp()
        self.case.assigned_assistant = self.assistant
        self.case.save()

        # Extra setup for documents
        self.document = Document.objects.create(
            case=self.case,
            firm=self.firm,
            uploaded_by=self.lawyer,
            file_name="test_doc.pdf",
            file_path=f"cases/{self.case.id}/{uuid.uuid4()}_test.pdf",
            file_size=1024,
            file_type="pdf",
            mime_type="application/pdf",
            category="court_filing",
            description="Test court filing",
            version=1
        )

        self.document2 = Document.objects.create(
            case=self.case2,
            firm=self.firm,
            uploaded_by=self.owner,
            file_name="contract.docx",
            file_path=f"cases/{self.case2.id}/{uuid.uuid4()}_contract.pdf",
            file_size=2048,
            file_type="docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            category="contract",
            version=1
        )

        # Shared document for testing share/revoke/expire
        self.shared_doc = Document.objects.create(
            case=self.case,
            firm=self.firm,
            uploaded_by=self.lawyer,
            file_name="shared.pdf",
            file_path=f"cases/{self.case.id}/{uuid.uuid4()}_shared.pdf",
            file_size=512,
            file_type="pdf",
            mime_type="application/pdf",
            category="evidence",
            is_shared=True,
            shared_link=uuid.uuid4(),
            shared_until=timezone.now() + timezone.timedelta(days=7),
            shared_by=self.lawyer,
            version=1
        )

        DocumentAccess.objects.create(
            document=self.document,
            accessed_by=self.lawyer,
            action="upload",
            ip_address="127.0.0.1",
            user_agent="test-agent",
        )
            

    # 1. Upload Document (POST upload_document_api)
    def test_lawyer_can_upload_to_assigned_case(self):
        self.client.force_authenticate(user=self.lawyer)
        url = reverse('upload_document_api', kwargs={'case_id': self.case.id})

        # Fake file
        file = SimpleUploadedFile("test_upload.pdf", b"fake pdf content", content_type="application/pdf")

        data = {
            "file": file,
            "category": "evidence",
            "description": "Test upload"
        }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["file_name"], "test_upload.pdf")

    def test_assistant_can_upload_to_assigned_case(self):
        self.client.force_authenticate(user=self.assistant)
        url = reverse('upload_document_api', kwargs={'case_id': self.case.id})  # assume case has assigned_assistant
        file = SimpleUploadedFile("assist_upload.pdf", b"content", content_type="application/pdf")
        data = {"file": file, "category": "correspondence"}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lawyer_cannot_upload_to_unassigned_case(self):
        self.client.force_authenticate(user=self.lawyer)
        url = reverse('upload_document_api', kwargs={'case_id': self.case2.id})  # not assigned
        file = SimpleUploadedFile("hack.pdf", b"content", content_type="application/pdf")
        data = {"file": file, "category": "evidence"}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_file_fails(self):
        self.client.force_authenticate(user=self.lawyer)
        url = reverse('upload_document_api', kwargs={'case_id': self.case.id})
        data = {"category": "evidence"}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("file", response.data)

    # 2. Get All Documents for Case (GET get_documents_api)
    def test_owner_sees_all_documents(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('get_documents_api', kwargs={'case_id': self.case.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # from setUp + any created

    def test_lawyer_sees_documents_on_assigned_case(self):
        self.client.force_authenticate(user=self.lawyer)
        url = reverse('get_documents_api', kwargs={'case_id': self.case.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lawyer_cannot_see_unassigned_case_documents(self):
        self.client.force_authenticate(user=self.lawyer)
        url = reverse('get_documents_api', kwargs={'case_id': self.case2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 3. View Document (GET view_document_api)
    def test_owner_can_view_document(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('view_document_api', kwargs={'document_id': self.document.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("url", response.data)
        self.assertIn("file_name", response.data)

    def test_client_can_view_own_case_document(self):
        self.client.force_authenticate(user=self.client_user)
        url = reverse('view_document_api', kwargs={'document_id': self.document.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # if CanAccessCase allows clients

    # 4. Share Document (POST share_document_api)
    def test_lawyer_can_share_document(self):
        self.client.force_authenticate(user=self.lawyer)
        url = reverse('share_document_api', kwargs={'document_id': self.document.id})
        data = {"shared_until": "2026-03-01T12:00:00Z"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("shared_link", response.data)
        self.document.refresh_from_db()
        self.assertTrue(self.document.is_shared)

    def test_assistant_cannot_share_unassigned_document(self):
        self.client.force_authenticate(user=self.assistant)
        url = reverse('share_document_api', kwargs={'document_id': self.document2.id})
        response = self.client.post(url, {"shared_until": "2026-03-01"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 5. Revoke Share (POST revoke_document_api)
    def test_owner_can_revoke_share(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('revoke_document_api', kwargs={'document_id': self.shared_doc.id})
        data = {"reason": "No longer needed"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.shared_doc.refresh_from_db()
        self.assertFalse(self.shared_doc.is_shared)
        self.assertIsNone(self.shared_doc.shared_link)

    # 6. Access via Shared Link (GET access_document_api)
    def test_public_can_access_valid_shared_link(self):
        url = reverse('access_document_api', kwargs={'shared_link': str(self.shared_doc.shared_link)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("url", response.data)

    def test_expired_shared_link_fails(self):
        self.shared_doc.shared_until = timezone.now() - timezone.timedelta(days=1)
        self.shared_doc.save()
        url = reverse('access_document_api', kwargs={'shared_link': str(self.shared_doc.shared_link)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("expired", response.data["error"])

    # 7. Document Access Logs (GET document_access_logs_api)
    def test_owner_can_view_access_logs(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('document_access_logs_api', kwargs={'document_id': self.document.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)  # at least upload log from setUp

    def test_lawyer_can_view_logs_on_assigned_document(self):
        self.client.force_authenticate(user=self.lawyer)
        url = reverse('document_access_logs_api', kwargs={'document_id': self.document.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_assistant_cannot_view_logs_on_unassigned_document(self):
        self.client.force_authenticate(user=self.assistant)
        url = reverse('document_access_logs_api', kwargs={'document_id': self.document2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

# Run with: python manage.py test system_management.tests.case_documents_test