from django.test import TestCase
from django.urls import reverse
from memos.models import Memo

class MemoViewTests(TestCase):
    def test_list_page_ok(self):
        res = self.client.get(reverse("memo_list"))
        self.assertEqual(res.status_code, 200)

    def test_create_requires_title(self):
        res = self.client.post(reverse("create_memo"), data={"title": "", "body": "x", "tags": ""})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "タイトルは必須")

    def test_search_by_title(self):
        """Test searching memos by title using ORM"""
        Memo.objects.create(title="Test Memo", body="Content")
        Memo.objects.create(title="Another Memo", body="Different")
        
        res = self.client.get(reverse("memo_list"), {"q": "Test"})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Test Memo")
        self.assertNotContains(res, "Another Memo")

    def test_search_by_body(self):
        """Test searching memos by body content using ORM"""
        Memo.objects.create(title="First", body="Test Content")
        Memo.objects.create(title="Second", body="Other Content")
        
        res = self.client.get(reverse("memo_list"), {"q": "Test"})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "First")
        self.assertNotContains(res, "Second")

    def test_search_with_special_characters(self):
        """Test that search handles special characters safely (no SQL injection)"""
        Memo.objects.create(title="Safe Memo", body="Normal content")
        
        # These should not cause SQL errors
        res = self.client.get(reverse("memo_list"), {"q": "'"})
        self.assertEqual(res.status_code, 200)
        
        res = self.client.get(reverse("memo_list"), {"q": "'; DROP TABLE memos_memo; --"})
        self.assertEqual(res.status_code, 200)
        
        res = self.client.get(reverse("memo_list"), {"q": "%"})
        self.assertEqual(res.status_code, 200)

    def test_search_returns_multiple_matches(self):
        """Test that search returns all matching memos"""
        Memo.objects.create(title="Python Tutorial", body="Learn Python")
        Memo.objects.create(title="Java Guide", body="Python comparison")
        Memo.objects.create(title="Ruby Basics", body="Ruby tutorial")
        
        res = self.client.get(reverse("memo_list"), {"q": "Python"})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Python Tutorial")
        self.assertContains(res, "Java Guide")
        self.assertNotContains(res, "Ruby Basics")

    # TODO: detail/edit/delete / legacy検索 / pagination のテストを追加
