# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'ExamResponse.expiration_days'
        db.delete_column(u'exam_examresponse', 'expiration_days')

        # Adding field 'ExamResponse.expiration_datetime'
        db.add_column(u'exam_examresponse', 'expiration_datetime',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 8, 26, 0, 0)),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'ExamResponse.expiration_days'
        db.add_column(u'exam_examresponse', 'expiration_days',
                      self.gf('django.db.models.fields.IntegerField')(default=7),
                      keep_default=False)

        # Deleting field 'ExamResponse.expiration_datetime'
        db.delete_column(u'exam_examresponse', 'expiration_datetime')


    models = {
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'randomize': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'exam.examresponse': {
            'Meta': {'object_name': 'ExamResponse'},
            'expiration_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'is_available': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'primary_key': 'True'}),
            'respondent': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        u'exam.freeresponsequestion': {
            'Meta': {'object_name': 'FreeResponseQuestion'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'exam': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.Exam']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'optional': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'rank': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        u'exam.freeresponseresponse': {
            'Meta': {'object_name': 'FreeResponseResponse'},
            'exam_response': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.ExamResponse']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.FreeResponseQuestion']"}),
            'response': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'})
        },
        u'exam.multiplechoiceoption': {
            'Meta': {'object_name': 'MultipleChoiceOption'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.MultipleChoiceQuestion']"}),
            'rank': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'exam.multiplechoicequestion': {
            'Meta': {'object_name': 'MultipleChoiceQuestion'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'exam': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.Exam']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'optional': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'randomize': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rank': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        u'exam.multiplechoiceresponse': {
            'Meta': {'object_name': 'MultipleChoiceResponse'},
            'exam_response': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.ExamResponse']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.MultipleChoiceOption']", 'null': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.MultipleChoiceQuestion']"})
        }
    }

    complete_apps = ['exam']