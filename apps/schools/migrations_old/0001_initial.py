# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'School'
        db.create_table('schools_school', (
            ('group_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.Group'], unique=True, primary_key=True)),
            ('school_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('address_line_one', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('address_line_two', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('address_city', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('address_state', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('address_country', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('school_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('gender_flag', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
        ))
        db.send_create_signal('schools', ['School'])

        # Adding model 'UserProfile'
        db.create_table('schools_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='knet_profile', unique=True, to=orm['auth.User'])),
            ('personal_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('home_address', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('access_token', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('khan_user_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('default_school', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='users_with_this_default', null=True, to=orm['schools.School'])),
        ))
        db.send_create_signal('schools', ['UserProfile'])

        # Adding model 'Classroom'
        db.create_table('schools_classroom', (
            ('group_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.Group'], unique=True, primary_key=True)),
            ('class_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('class_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(related_name='classrooms', to=orm['schools.School'])),
        ))
        db.send_create_signal('schools', ['Classroom'])

        # Adding model 'Challenge'
        db.create_table('schools_challenge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('challenge_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('classroom', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='challenges', null=True, to=orm['schools.Classroom'])),
        ))
        db.send_create_signal('schools', ['Challenge'])

        # Adding model 'ClassroomTeam'
        db.create_table('schools_classroomteam', (
            ('group_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.Group'], unique=True, primary_key=True)),
            ('classroom', self.gf('django.db.models.fields.related.ForeignKey')(related_name='teams', to=orm['schools.Classroom'])),
            ('team_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('challenge_complete_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('exercise_complete_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('schools', ['ClassroomTeam'])

        # Adding model 'GroupChallenge'
        db.create_table('schools_groupchallenge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('classroom_team', self.gf('django.db.models.fields.related.ForeignKey')(related_name='group_challenges', to=orm['schools.ClassroomTeam'])),
            ('challenge', self.gf('django.db.models.fields.related.ForeignKey')(related_name='challenge_groups', to=orm['schools.Challenge'])),
        ))
        db.send_create_signal('schools', ['GroupChallenge'])

        # Adding model 'ChallengeExercise'
        db.create_table('schools_challengeexercise', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('challenge', self.gf('django.db.models.fields.related.ForeignKey')(related_name='exercises', to=orm['schools.Challenge'])),
            ('exercise_name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('exercise_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('exercise_description', self.gf('django.db.models.fields.CharField')(max_length=2000, null=True, blank=True)),
        ))
        db.send_create_signal('schools', ['ChallengeExercise'])

        # Adding model 'ClassInvitation'
        db.create_table('schools_classinvitation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('school_class', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invitations', to=orm['schools.Classroom'])),
            ('invited_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invitations_received', to=orm['auth.User'])),
            ('invited_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invitations_sent', to=orm['auth.User'])),
            ('invited_on_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('rejected_on_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('accepted_on_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('schools', ['ClassInvitation'])


    def backwards(self, orm):
        # Deleting model 'School'
        db.delete_table('schools_school')

        # Deleting model 'UserProfile'
        db.delete_table('schools_userprofile')

        # Deleting model 'Classroom'
        db.delete_table('schools_classroom')

        # Deleting model 'Challenge'
        db.delete_table('schools_challenge')

        # Deleting model 'ClassroomTeam'
        db.delete_table('schools_classroomteam')

        # Deleting model 'GroupChallenge'
        db.delete_table('schools_groupchallenge')

        # Deleting model 'ChallengeExercise'
        db.delete_table('schools_challengeexercise')

        # Deleting model 'ClassInvitation'
        db.delete_table('schools_classinvitation')


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
        'schools.challenge': {
            'Meta': {'object_name': 'Challenge'},
            'challenge_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'classroom': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'challenges'", 'null': 'True', 'to': "orm['schools.Classroom']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'schools.challengeexercise': {
            'Meta': {'object_name': 'ChallengeExercise'},
            'challenge': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'exercises'", 'to': "orm['schools.Challenge']"}),
            'exercise_description': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'exercise_name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'exercise_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'schools.classinvitation': {
            'Meta': {'object_name': 'ClassInvitation'},
            'accepted_on_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invited_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invitations_sent'", 'to': "orm['auth.User']"}),
            'invited_on_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'invited_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invitations_received'", 'to': "orm['auth.User']"}),
            'rejected_on_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'school_class': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invitations'", 'to': "orm['schools.Classroom']"})
        },
        'schools.classroom': {
            'Meta': {'object_name': 'Classroom', '_ormbases': ['auth.Group']},
            'class_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'classrooms'", 'to': "orm['schools.School']"})
        },
        'schools.classroomteam': {
            'Meta': {'object_name': 'ClassroomTeam', '_ormbases': ['auth.Group']},
            'challenge_complete_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'challenges': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'teams'", 'symmetrical': 'False', 'through': "orm['schools.GroupChallenge']", 'to': "orm['schools.Challenge']"}),
            'classroom': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'teams'", 'to': "orm['schools.Classroom']"}),
            'exercise_complete_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'team_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'schools.groupchallenge': {
            'Meta': {'object_name': 'GroupChallenge'},
            'challenge': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'challenge_groups'", 'to': "orm['schools.Challenge']"}),
            'classroom_team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group_challenges'", 'to': "orm['schools.ClassroomTeam']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'schools.school': {
            'Meta': {'object_name': 'School', '_ormbases': ['auth.Group']},
            'address_city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address_country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'address_line_one': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address_line_two': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address_state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'gender_flag': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'school_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'school_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'schools.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'default_school': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'users_with_this_default'", 'null': 'True', 'to': "orm['schools.School']"}),
            'home_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'khan_user_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'personal_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'knet_profile'", 'unique': 'True', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['schools']