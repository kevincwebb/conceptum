# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TopicTag'
        db.create_table(u'interviews_topictag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'interviews', ['TopicTag'])

        # Adding M2M table for field excerpts on 'TopicTag'
        m2m_table_name = db.shorten_name(u'interviews_topictag_excerpts')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('topictag', models.ForeignKey(orm[u'interviews.topictag'], null=False)),
            ('conceptexcerpt', models.ForeignKey(orm[u'interviews.conceptexcerpt'], null=False))
        ))
        db.create_unique(m2m_table_name, ['topictag_id', 'conceptexcerpt_id'])

        # Adding model 'ConceptExcerpt'
        db.create_table(u'interviews_conceptexcerpt', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('interview', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['interviews.Interview'])),
            ('response', self.gf('django.db.models.fields.TextField')()),
            ('concept_tag', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ability_level', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('importance', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'interviews', ['ConceptExcerpt'])

        # Adding field 'InterviewGroup.is_concept'
        db.add_column(u'interviews_interviewgroup', 'is_concept',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Interview.is_concept'
        db.add_column(u'interviews_interview', 'is_concept',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'TopicTag'
        db.delete_table(u'interviews_topictag')

        # Removing M2M table for field excerpts on 'TopicTag'
        db.delete_table(db.shorten_name(u'interviews_topictag_excerpts'))

        # Deleting model 'ConceptExcerpt'
        db.delete_table(u'interviews_conceptexcerpt')

        # Deleting field 'InterviewGroup.is_concept'
        db.delete_column(u'interviews_interviewgroup', 'is_concept')

        # Deleting field 'Interview.is_concept'
        db.delete_column(u'interviews_interview', 'is_concept')


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
        u'interviews.conceptexcerpt': {
            'Meta': {'object_name': 'ConceptExcerpt'},
            'ability_level': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'concept_tag': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'interview': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['interviews.Interview']"}),
            'response': ('django.db.models.fields.TextField', [], {})
        },
        u'interviews.dummyconcept': {
            'Meta': {'object_name': 'DummyConcept'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '31'})
        },
        u'interviews.excerpt': {
            'Meta': {'object_name': 'Excerpt'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interview': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['interviews.Interview']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'response': ('django.db.models.fields.TextField', [], {})
        },
        u'interviews.interview': {
            'Meta': {'object_name': 'Interview'},
            'date_of_interview': ('django.db.models.fields.DateField', [], {}),
            'date_uploaded': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['interviews.InterviewGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interviewee': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'is_concept': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'uploaded_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authtools.User']"})
        },
        u'interviews.interviewgroup': {
            'Meta': {'object_name': 'InterviewGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_concept': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'unlocked': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'interviews.topictag': {
            'Meta': {'object_name': 'TopicTag'},
            'excerpts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['interviews.ConceptExcerpt']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['interviews']