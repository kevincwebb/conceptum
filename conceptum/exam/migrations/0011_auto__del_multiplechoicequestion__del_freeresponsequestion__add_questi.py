# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'MultipleChoiceQuestion'
        db.delete_table(u'exam_multiplechoicequestion')

        # Deleting model 'FreeResponseQuestion'
        db.delete_table(u'exam_freeresponsequestion')

        # Adding model 'Question'
        db.create_table(u'exam_question', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('exam', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exam.Exam'])),
            ('is_multiple_choice', self.gf('django.db.models.fields.BooleanField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('question', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('number', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('rank', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('optional', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'exam', ['Question'])


        # Changing field 'FreeResponseResponse.question'
        db.alter_column(u'exam_freeresponseresponse', 'question_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exam.Question']))

        # Changing field 'MultipleChoiceOption.question'
        db.alter_column(u'exam_multiplechoiceoption', 'question_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exam.Question']))

        # Changing field 'MultipleChoiceResponse.question'
        db.alter_column(u'exam_multiplechoiceresponse', 'question_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exam.Question']))

    def backwards(self, orm):
        # Adding model 'MultipleChoiceQuestion'
        db.create_table(u'exam_multiplechoicequestion', (
            ('exam', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exam.Exam'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('rank', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('randomize', self.gf('django.db.models.fields.BooleanField')(default=False)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('optional', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('question', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'exam', ['MultipleChoiceQuestion'])

        # Adding model 'FreeResponseQuestion'
        db.create_table(u'exam_freeresponsequestion', (
            ('rank', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('exam', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exam.Exam'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('question', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('optional', self.gf('django.db.models.fields.BooleanField')(default=False)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('number', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal(u'exam', ['FreeResponseQuestion'])

        # Deleting model 'Question'
        db.delete_table(u'exam_question')


        # Changing field 'FreeResponseResponse.question'
        db.alter_column(u'exam_freeresponseresponse', 'question_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exam.FreeResponseQuestion']))

        # Changing field 'MultipleChoiceOption.question'
        db.alter_column(u'exam_multiplechoiceoption', 'question_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exam.MultipleChoiceQuestion']))

        # Changing field 'MultipleChoiceResponse.question'
        db.alter_column(u'exam_multiplechoiceresponse', 'question_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exam.MultipleChoiceQuestion']))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'authtools.user': {
            'Meta': {'ordering': "[u'name', u'email']", 'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'exam.exam': {
            'Meta': {'object_name': 'Exam'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'randomize': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'stage': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'exam.examresponse': {
            'Meta': {'object_name': 'ExamResponse'},
            'expiration_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'primary_key': 'True'}),
            'respondent': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'response_set': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.ResponseSet']"}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'submitted': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        u'exam.freeresponseresponse': {
            'Meta': {'object_name': 'FreeResponseResponse'},
            'exam_response': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.ExamResponse']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.Question']"}),
            'response': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'})
        },
        u'exam.multiplechoiceoption': {
            'Meta': {'ordering': "['index']", 'object_name': 'MultipleChoiceOption'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {}),
            'is_correct': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.Question']"}),
            'rank': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'exam.multiplechoiceresponse': {
            'Meta': {'object_name': 'MultipleChoiceResponse'},
            'exam_response': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.ExamResponse']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.MultipleChoiceOption']", 'null': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.Question']"})
        },
        u'exam.question': {
            'Meta': {'object_name': 'Question'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'exam': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.Exam']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'is_multiple_choice': ('django.db.models.fields.BooleanField', [], {}),
            'number': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'optional': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'rank': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'exam.responseset': {
            'Meta': {'ordering': "['-created']", 'object_name': 'ResponseSet'},
            'course': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'exam': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.Exam']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.ContributorProfile']"}),
            'pre_test': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'profiles.contributorprofile': {
            'Meta': {'object_name': 'ContributorProfile'},
            'homepage': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'interest_in_deploy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'interest_in_devel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_contrib': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text_info': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'to': u"orm['authtools.User']"})
        }
    }

    complete_apps = ['exam']