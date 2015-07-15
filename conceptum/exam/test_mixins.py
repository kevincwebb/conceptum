from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import SimpleTestCase
from django.utils import timezone

from interviews.models import get_concept_list, DummyConcept as Concept
from profiles.tests import set_up_user

from .models import Exam, FreeResponseQuestion, ExamStage, ExamKind, ResponseSet, ExamResponse

    
class CurrentAppMixinTest(SimpleTestCase):
    """
    We use ExamCreateView to test this Mixin
    """
    def setUp(self):
        self.user = set_up_user()
        self.user.is_staff = True
        self.user.save()
        self.client.login(email=self.user.email, password='password')
        
    def test_survey(self):
        response = self.client.get(reverse('survey:create'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['current_app'], 'survey')
        
        response = self.client.post(reverse('survey:create'),{'name':'exam','description':'blah'})
        self.assertRedirects(response, reverse('survey:index'))
    
    def test_CI(self):
        response = self.client.get(reverse('CI_exam:create'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['current_app'], 'CI')
        
        response = self.client.post(reverse('CI_exam:create'),{'name':'exam','description':'blah'})
        self.assertRedirects(response, reverse('CI_exam:index'))


class DevelopmentMixinTest(SimpleTestCase):
    def setUp(self):
        get_concept_list()
        self.exam, created = Exam.objects.get_or_create(name='Dev Exam',
                                                        description='Blah blah blah.',
                                                        stage=ExamStage.DEV,
                                                        kind=ExamKind.CI)
        self.user = set_up_user()
        self.user.is_staff = True
        self.user.save()
        self.client.login(email=self.user.email, password='password')
        
    def test_exam_kwarg(self):
        """
        Uses url kwarg 'exam_id' to get the exam object (DevDetailView)
        """
        response = self.client.get(reverse('CI_exam:detail', args=[self.exam.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_question_kwarg(self):
        """
        Use url kwarg 'question_id' to get the exam object (FreeResponseEditView)
        """
        concept_type = ContentType.objects.get_for_model(Concept)
        concept = Concept.objects.get(name = "Concept A")
        question = FreeResponseQuestion.objects.create(
            exam=self.exam,
            question="A free response question?",
            content_type=concept_type,
            object_id=concept.id)
        response = self.client.get(reverse('CI_exam:fr_edit', args=[question.id]))
        self.assertEqual(response.status_code, 200)
        
    def test_exam_stage(self):
        """
        Try to view exam that is not in the DEV stage
        """
        exam = Exam.objects.create(name='Wrong Exam for Dev',
                                   description='Blah blah blah.',
                                   stage=ExamStage.DIST,
                                   kind=ExamKind.CI)
        response = self.client.get(reverse('CI_exam:detail', args=[exam.id]))
        self.assertEqual(response.status_code, 403)
        
        exam.stage=ExamStage.CLOSED
        exam.save()
        response = self.client.get(reverse('CI_exam:detail', args=[exam.id]))
        self.assertEqual(response.status_code, 403)
    
    def test_exam_kind(self):
        """
        Try to view an exam using the wrong namespace
        """
        response = self.client.get(reverse('survey:detail', args=[self.exam.id]))
        self.assertEqual(response.status_code, 403)


class DistributeMixinTest(SimpleTestCase):
    def setUp(self):
        get_concept_list()
        self.exam, created = Exam.objects.get_or_create(name='Dist Exam',
                                                        description='Blah blah blah.',
                                                        stage=ExamStage.DIST,
                                                        kind=ExamKind.CI)
        self.user = set_up_user()
        self.user.is_staff = True
        self.user.save()
        self.client.login(email=self.user.email, password='password')
        
    def test_exam_kwarg(self):
        """
        Uses url kwarg 'exam_id' to get the exam object (DistDetailView)
        """
        response = self.client.get(reverse('CI_exam:distribute_detail', args=[self.exam.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_response_set_kwarg(self):
        """
        Use url kwarg 'rs_id' to get the exam object (ResponseSetDetailView)
        """
        response_set = ResponseSet.objects.create(exam=self.exam,
                                                  course='CS150',
                                                  instructor=self.user.profile)
        response = self.client.get(reverse('CI_exam:responses', args=[response_set.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_exam_response_kwarg(self):
        """
        Use url kwarg 'key' to get the exam object (ExamResponseDetailView)
        """
        response_set = ResponseSet.objects.create(exam=self.exam,
                                                  course='CS150',
                                                  instructor=self.user.profile)
        exam_response = ExamResponse.objects.create(response_set=response_set,
                                                    expiration_datetime=timezone.now())
        response = self.client.get(reverse('CI_exam:response_detail', args=[exam_response.key]))
        self.assertEqual(response.status_code, 200)
        
    def test_exam_stage(self):
        """
        Try to view exam that is not in the DIST stage
        """
        exam = Exam.objects.create(name='Wrong Exam for Dist',
                                   description='Blah blah blah.',
                                   stage=ExamStage.DEV,
                                   kind=ExamKind.CI)
        response = self.client.get(reverse('CI_exam:distribute_detail', args=[exam.id]))
        self.assertEqual(response.status_code, 403)
        
        exam.stage=ExamStage.CLOSED
        exam.save()
        response = self.client.get(reverse('CI_exam:distribute_detail', args=[exam.id]))
        self.assertEqual(response.status_code, 403)
    
    def test_exam_kind(self):
        """
        Try to view an exam using the wrong namespace
        """
        response = self.client.get(reverse('survey:distribute_detail', args=[self.exam.id]))
        self.assertEqual(response.status_code, 403)



