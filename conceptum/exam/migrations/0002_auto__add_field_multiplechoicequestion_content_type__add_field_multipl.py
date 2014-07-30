# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'MultipleChoiceQuestion.content_type'
        db.add_column(u'exam_multiplechoicequestion', 'content_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(default='', to=orm['contenttypes.ContentType']),
                      keep_default=False)

        # Adding field 'MultipleChoiceQuestion.object_id'
        db.add_column(u'exam_multiplechoicequestion', 'object_id',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'FreeResponseQuestion.content_type'
        db.add_column(u'exam_freeresponsequestion', 'content_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(default='', to=orm['contenttypes.ContentType']),
                      keep_default=False)

        # Adding field 'FreeResponseQuestion.object_id'
        db.add_column(u'exam_freeresponsequestion', 'object_id',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'MultipleChoiceQuestion.content_type'
        db.delete_column(u'exam_multiplechoicequestion', 'content_type_id')

        # Deleting field 'MultipleChoiceQuestion.object_id'
        db.delete_column(u'exam_multiplechoicequestion', 'object_id')

        # Deleting field 'FreeResponseQuestion.content_type'
        db.delete_column(u'exam_freeresponsequestion', 'content_type_id')

        # Deleting field 'FreeResponseQuestion.object_id'
        db.delete_column(u'exam_freeresponsequestion', 'object_id')


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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.FreeResponseQuestion']"}),
            'response': ('django.db.models.fields.CharField', [], {'max_length': '2000'})
        },
        u'exam.multiplechoiceoption': {
            'Meta': {'object_name': 'MultipleChoiceOption'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.FreeResponseQuestion']"}),
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.MultipleChoiceOption']"}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.MultipleChoiceQuestion']"})
        }
    }

    complete_apps = ['exam']