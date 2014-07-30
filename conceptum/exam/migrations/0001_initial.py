# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Exam'
        db.create_table(u'exam_exam', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('randomize', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'exam', ['Exam'])

        # Adding model 'FreeResponseQuestion'
        db.create_table(u'exam_freeresponsequestion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('exam', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exam.Exam'])),
            ('question', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('rank', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('optional', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'exam', ['FreeResponseQuestion'])

        # Adding model 'FreeResponseResponse'
        db.create_table(u'exam_freeresponseresponse', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exam.FreeResponseQuestion'])),
            ('response', self.gf('django.db.models.fields.CharField')(max_length=2000)),
        ))
        db.send_create_signal(u'exam', ['FreeResponseResponse'])

        # Adding model 'MultipleChoiceQuestion'
        db.create_table(u'exam_multiplechoicequestion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('exam', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exam.Exam'])),
            ('question', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('rank', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('optional', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('randomize', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'exam', ['MultipleChoiceQuestion'])

        # Adding model 'MultipleChoiceOption'
        db.create_table(u'exam_multiplechoiceoption', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exam.FreeResponseQuestion'])),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('rank', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal(u'exam', ['MultipleChoiceOption'])

        # Adding model 'MultipleChoiceResponse'
        db.create_table(u'exam_multiplechoiceresponse', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exam.MultipleChoiceQuestion'])),
            ('option', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exam.MultipleChoiceOption'])),
        ))
        db.send_create_signal(u'exam', ['MultipleChoiceResponse'])


    def backwards(self, orm):
        # Deleting model 'Exam'
        db.delete_table(u'exam_exam')

        # Deleting model 'FreeResponseQuestion'
        db.delete_table(u'exam_freeresponsequestion')

        # Deleting model 'FreeResponseResponse'
        db.delete_table(u'exam_freeresponseresponse')

        # Deleting model 'MultipleChoiceQuestion'
        db.delete_table(u'exam_multiplechoicequestion')

        # Deleting model 'MultipleChoiceOption'
        db.delete_table(u'exam_multiplechoiceoption')

        # Deleting model 'MultipleChoiceResponse'
        db.delete_table(u'exam_multiplechoiceresponse')


    models = {
        u'exam.exam': {
            'Meta': {'object_name': 'Exam'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'randomize': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'exam.freeresponsequestion': {
            'Meta': {'object_name': 'FreeResponseQuestion'},
            'exam': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.Exam']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
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
            'exam': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.Exam']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
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