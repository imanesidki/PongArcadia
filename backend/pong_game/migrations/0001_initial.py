# Generated by Django 5.1.6 on 2025-03-12 03:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('theme', models.CharField(choices=[('fire', 'Fire'), ('water', 'Water')], default='fire', max_length=10)),
                ('difficulty', models.CharField(choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='medium', max_length=10)),
                ('status', models.CharField(choices=[('waiting', 'Waiting for Players'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='waiting', max_length=15)),
                ('final_score_player1', models.IntegerField(default=0)),
                ('final_score_player2', models.IntegerField(default=0)),
                ('player1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games_as_player1', to=settings.AUTH_USER_MODEL)),
                ('player2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='games_as_player2', to=settings.AUTH_USER_MODEL)),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='games_won', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_number', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('in_progress', 'In Progress'), ('completed', 'Completed')], default='in_progress', max_length=15)),
                ('score_player1', models.IntegerField(default=0)),
                ('score_player2', models.IntegerField(default=0)),
                ('winner', models.CharField(blank=True, choices=[('player1', 'Player 1'), ('player2', 'Player 2')], max_length=10, null=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='pong_game.game')),
            ],
            options={
                'ordering': ['game', 'match_number'],
                'unique_together': {('game', 'match_number')},
            },
        ),
    ]
