# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserHistory'
        db.create_table('usermanagement_userhistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('event', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('event_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('usermanagement', ['UserHistory'])

        # Adding model 'Class'
        db.create_table('usermanagement_class', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'], unique=True)),
            ('class_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('class_description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('usermanagement', ['Class'])

        # Adding model 'School'
        db.create_table('usermanagement_school', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('school_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('address_line_one', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('address_line_two', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('address_city', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('address_state', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('address_country', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('school_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('gender_flag', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
        ))
        db.send_create_signal('usermanagement', ['School'])

        # Adding M2M table for field classes on 'School'
        db.create_table('usermanagement_school_classes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('school', models.ForeignKey(orm['usermanagement.school'], null=False)),
            ('class', models.ForeignKey(orm['usermanagement.class'], null=False))
        ))
        db.create_unique('usermanagement_school_classes', ['school_id', 'class_id'])

        # Adding M2M table for field users on 'School'
        db.create_table('usermanagement_school_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('school', models.ForeignKey(orm['usermanagement.school'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('usermanagement_school_users', ['school_id', 'user_id'])

        # Adding model 'UserProfile'
        db.create_table('usermanagement_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('personal_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('home_address', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal('usermanagement', ['UserProfile'])

    def backwards(self, orm):
        # Deleting model 'UserHistory'
        db.delete_table('usermanagement_userhistory')

        # Deleting model 'Class'
        db.delete_table('usermanagement_class')

        # Deleting model 'School'
        db.delete_table('usermanagement_school')

        # Removing M2M table for field classes on 'School'
        db.delete_table('usermanagement_school_classes')

        # Removing M2M table for field users on 'School'
        db.delete_table('usermanagement_school_users')

        # Deleting model 'UserProfile'
        db.delete_table('usermanagement_userprofile')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'usermanagement.class': {
            'Meta': {'object_name': 'Class'},
            'class_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'usermanagement.school': {
            'Meta': {'object_name': 'School'},
            'address_city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address_country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'address_line_one': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address_line_two': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address_state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'classes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['usermanagement.Class']", 'symmetrical': 'False', 'blank': 'True'}),
            'gender_flag': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'school_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'school_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'usermanagement.userhistory': {
            'Meta': {'object_name': 'UserHistory'},
            'event': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'event_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'usermanagement.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'home_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'personal_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['usermanagement']