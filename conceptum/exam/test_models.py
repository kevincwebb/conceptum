from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db import models
from django.test import SimpleTestCase
from django.utils.translation import ugettext_lazy as _

import reversion

from .models import Exam, FreeResponseQuestion, MultipleChoiceQuestion, MultipleChoiceOption


class DummyConcept(models.Model):
    """
    Since Questions are related to Concept by generic foreign key, we can use
    this simple model instead of importing.
    """
    name = models.CharField(max_length=31, unique=True)
    
    def __str__(self):
        return self.name

def create_concepts():
    """
    Creates 4 concepts for use in testing.
    Does not return anything, queryset accessible via objects.all()
    """
    for x in ['A','B','C','D']:
        DummyConcept.objects.get_or_create(name="Concept %s" % x)
        

class ModelsTest(SimpleTestCase):
    def setUp(self):
        create_concepts()
 
    def test_fr_get_unique_versions(self):
        # Reversion registration through the admin interface does not work in tests,
        # nor does ReversionMiddleware work to create revisions
        exam, created = Exam.objects.get_or_create(name='Test Exam',
                                                   description='an exam for testing')
        concept_type = ContentType.objects.get_for_model(DummyConcept)
        concept = DummyConcept.objects.get(name = "Concept A")
        
        # Check that initial version appears in the list
        with reversion.create_revision():
            question = FreeResponseQuestion.objects.create(exam=exam,
                                                           question="Version 1 ?",
                                                           number=1,
                                                           content_type=concept_type,
                                                           object_id=concept.id,
                                                           id=3478)
        self.assertEqual(len(question.get_unique_versions()),1)
        self.assertEqual(question.get_unique_versions()[0], reversion.get_for_object(question)[0])
        
        # Save question, should create another version. Since they are identical,
        # our unique list should only have 1 version
        with reversion.create_revision():
            question.save()
        self.assertEqual(len(reversion.get_for_object(question)), 2)
        self.assertEqual(len(question.get_unique_versions()), 1)
        
        # Change the question, the unique list should have 2 versions, newest first
        with reversion.create_revision():
            question.question="Version 2 ?"
            question.save()
        self.assertEqual(len(reversion.get_for_object(question)), 3)
        self.assertEqual(len(question.get_unique_versions()), 2)
        self.assertEqual(question.get_unique_versions()[0].field_dict['question'],"Version 2 ?")
        
        # Revert to current version, unique list shouldn't change
        with reversion.create_revision():
            question.get_unique_versions()[0].revert()
        self.assertEqual(len(reversion.get_for_object(question)), 4)
        self.assertEqual(len(question.get_unique_versions()), 2)
        
        # Revert to old version, unique list should still only have 2 items,
        # reverted version first
        with reversion.create_revision():
            question.get_unique_versions()[1].revert()
        self.assertEqual(len(reversion.get_for_object(question)), 5)
        self.assertEqual(len(question.get_unique_versions()), 2)
        self.assertEqual(question.get_unique_versions()[0].field_dict['question'],"Version 1 ?")
    
    def test_mc_get_unique_versions(self):
        """
        Because MCQ and FRQ use the same get_unique_versions function, this test does not
        repeat tests done by test_fr_get_unique_versions
        """
        exam, created = Exam.objects.get_or_create(name='Test Exam',
                                                   description='an exam for testing')
        concept_type = ContentType.objects.get_for_model(DummyConcept)
        option_type = ContentType.objects.get_for_model(MultipleChoiceOption)
        concept = DummyConcept.objects.get(name = "Concept A")
        
        # Check that initial version appears in the list
        with reversion.create_revision():
            question = MultipleChoiceQuestion.objects.create(exam=exam,
                                                             question="Version 1 ?",
                                                             number=1,
                                                             content_type=concept_type,
                                                             object_id=concept.id,
                                                             id=1578)
            option_1 = MultipleChoiceOption.objects.create(question=question,
                                                           index=1,
                                                           text="A v1")
            option_2 = MultipleChoiceOption.objects.create(question=question,
                                                           index=2,
                                                           text="B v1")
        self.assertEqual(len(question.get_unique_versions()),1)
        self.assertEqual(question.get_unique_versions()[0], reversion.get_for_object(question)[0])
        
        # Change an option, should make a new unique version
        with reversion.create_revision():
            option_1.text = "A v2"
            option_1.save()
            question.save()
        self.assertEqual(len(question.get_unique_versions()),2)
        
        # Add an option, should make a new unique version
        with reversion.create_revision():
            option_3 = MultipleChoiceOption.objects.create(question=question,
                                                           index=3,
                                                           text="C v1")
            option_3.save()
            question.save()
        self.assertEqual(len(question.get_unique_versions()),3)
        option_versions = question.get_unique_versions()[0].revision.version_set.filter(
            content_type__pk=option_type.id)
        options = (option.object for option in option_versions)
        self.assertIn(option_3, options)
        
        # Save question and options, should not make a new unique version
        with reversion.create_revision():
            option_1.save()
            option_2.save()
            option_3.save()
            question.save()
        self.assertEqual(len(question.get_unique_versions()),3)
        
        # Revert, should delete an option but not make new unique version
        with reversion.create_revision():
            revision = question.get_unique_versions()[1].revision
            question.revision_revert(revision)
        self.assertEqual(len(question.get_unique_versions()),3)
        self.assertNotIn(option_3, MultipleChoiceOption.objects.all())
        
        # Revert back, option_3 should exist again
        with reversion.create_revision():
            revision = question.get_unique_versions()[1].revision
            question.revision_revert(revision)
        self.assertEqual(len(question.get_unique_versions()),3)
        self.assertIn(option_3, MultipleChoiceOption.objects.all())
        
        # Delete option_3 manally, doesn't create a new unique version
        with reversion.create_revision():
            option_3.delete()
            question.save()
        self.assertEqual(len(question.get_unique_versions()),3)
        
        # Revert back, option_3 is recreated
        # Note, we have to 'get' the object because out local variable points to
        # an object that was deleted
        with reversion.create_revision():
            revision = question.get_unique_versions()[1].revision
            question.revision_revert(revision)
        self.assertEqual(len(question.get_unique_versions()),3)
        option_3 = MultipleChoiceOption.objects.get(text="C v1")
        self.assertIn(option_3, MultipleChoiceOption.objects.all())
        
        # Delete an option manually, creates new unique version
        with reversion.create_revision():
            option_1.delete()
            question.save()
        self.assertEqual(len(question.get_unique_versions()),4)
        self.assertNotIn(option_1, MultipleChoiceOption.objects.all())
        
        # Swap option texts. This should create a new unique version, because option
        # versions are compared by their serialized data, not just text
        with reversion.create_revision():
            option_2.text = "C v1"
            option_3.text = "B v1"
            option_2.save()
            option_3.save()
            question.save()
        self.assertEqual(len(question.get_unique_versions()),5)
        
        # Swap option order
        with reversion.create_revision():
            option_2.index = 2
            option_3.index = 1
            option_2.save()
            option_3.save()
            question.save()
        self.assertEqual(len(question.get_unique_versions()),6)