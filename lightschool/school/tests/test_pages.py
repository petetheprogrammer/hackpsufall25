from django.test import TestCase, Client

class PageTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'LightSchool')

    def test_subject_grade_page(self):
        response = self.client.get('/subject/math/grade/1/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Units')

    def test_lesson_page(self):
        response = self.client.get('/lesson/math/1/add_basics/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Addition Basics')

    def test_quiz_page(self):
        response = self.client.get('/quiz/math/1/add_basics/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Quiz')