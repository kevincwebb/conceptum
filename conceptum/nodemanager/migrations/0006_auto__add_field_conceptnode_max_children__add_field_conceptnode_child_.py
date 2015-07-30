# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ConceptNode.max_children'
        db.add_column(u'nodemanager_conceptnode', 'max_children',
                      self.gf('django.db.models.fields.IntegerField')(default=5),
                      keep_default=False)

        # Adding field 'ConceptNode.child_typename'
        db.add_column(u'nodemanager_conceptnode', 'child_typename',
                      self.gf('django.db.models.fields.CharField')(default='unnamed', max_length=50),
                      keep_default=False)


        # Changing field 'ConceptNode.node_type'
        db.alter_column(u'nodemanager_conceptnode', 'node_type', self.gf('django.db.models.fields.CharField')(max_length=1))
        # Removing M2M table for field admins on 'CITreeInfo'
        db.delete_table(db.shorten_name(u'nodemanager_citreeinfo_admins'))

        # Removing M2M table for field users on 'CITreeInfo'
        db.delete_table(db.shorten_name(u'nodemanager_citreeinfo_users'))


    def backwards(self, orm):
        # Deleting field 'ConceptNode.max_children'
        db.delete_column(u'nodemanager_conceptnode', 'max_children')

        # Deleting field 'ConceptNode.child_typename'
        db.delete_column(u'nodemanager_conceptnode', 'child_typename')


        # Changing field 'ConceptNode.node_type'
        db.alter_column(u'nodemanager_conceptnode', 'node_type', self.gf('django.db.models.fields.CharField')(max_length=2))
        # Adding M2M table for field admins on 'CITreeInfo'
        m2m_table_name = db.shorten_name(u'nodemanager_citreeinfo_admins')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('citreeinfo', models.ForeignKey(orm[u'nodemanager.citreeinfo'], null=False)),
            ('user', models.ForeignKey(orm[u'authtools.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['citreeinfo_id', 'user_id'])

        # Adding M2M table for field users on 'CITreeInfo'
        m2m_table_name = db.shorten_name(u'nodemanager_citreeinfo_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('citreeinfo', models.ForeignKey(orm[u'nodemanager.citreeinfo'], null=False)),
            ('user', models.ForeignKey(orm[u'authtools.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['citreeinfo_id', 'user_id'])


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
        u'nodemanager.citreeinfo': {
            'Meta': {'object_name': 'CITreeInfo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_master': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'nodemanager.conceptatom': {
            'Meta': {'object_name': 'ConceptAtom'},
            'concept_node': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nodemanager.ConceptNode']"}),
            'final_choice': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'merged_atoms': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nodemanager.ConceptAtom']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authtools.User']"})
        },
        u'nodemanager.conceptnode': {
            'Meta': {'object_name': 'ConceptNode'},
            'child_typename': ('django.db.models.fields.CharField', [], {'default': "'unnamed'", 'max_length': '50'}),
            'ci_tree_info': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nodemanager.CITreeInfo']"}),
            'content': ('django.db.models.fields.TextField', [], {'max_length': '140'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'max_children': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'node_type': ('django.db.models.fields.CharField', [], {'default': "'F'", 'max_length': '1'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': u"orm['nodemanager.ConceptNode']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['authtools.User']", 'symmetrical': 'False'})
        }
    }

    complete_apps = ['nodemanager']