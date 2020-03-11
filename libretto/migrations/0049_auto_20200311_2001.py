# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-03-11 19:01
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
from tree.operations import DeleteTreeTrigger, CreateTreeTrigger, RebuildPaths

import libretto.models.base


def update_oeuvre_numero_extrait(apps, schema_editor):
    Oeuvre = apps.get_model('libretto.Oeuvre')
    for oeuvre in Oeuvre.objects.all():
        oeuvre.save(update_fields=['numero_extrait'])


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0048_auto_20200302_1917'),
    ]

    operations = [
        DeleteTreeTrigger('oeuvre', parent_field='extrait_de'),
        migrations.AlterField(
            model_name='oeuvre',
            name='numero',
            field=libretto.models.base.NumberCharField(blank=True, db_index=True, help_text='Exemple\xa0: «\xa05\xa0» pour symphonie n°\xa05, «\xa07a\xa0» pour valse n°\xa07\u202fa, ou encore «\xa03-7\xa0» pour sonates n°\xa03 à\xa07. <strong>Ne pas confondre avec le sous-numéro d’opus.</strong>', max_length=10, validators=[django.core.validators.RegexValidator('^[\\d\\w\\-]+$', 'Vous ne pouvez saisir que des chiffres, lettres non accentuées et tiret, le tout sans espace.')], verbose_name='numéro'),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='numero_extrait',
            field=libretto.models.base.NumberCharField(blank=True, db_index=True, help_text='Le numéro de l’extrait au sein de l’œuvre, par exemple «\xa03\xa0» pour le 3<sup>e</sup> mouvement d’un concerto, «\xa04\xa0» pour l’acte IV d’un opéra, ou encore «\xa012b\xa0».', max_length=10, validators=[django.core.validators.RegexValidator('^([1-9]\\d*)([^\\d\\.\\-]*)$', 'Vous devez saisir un nombre en chiffres arabes éventellement suivi de lettres.')], verbose_name='numéro d’extrait'),
        ),
        migrations.AlterField(
            model_name='source',
            name='lieu_conservation',
            field=models.CharField(blank=True, db_index=True, max_length=75, verbose_name='lieu de conservation'),
        ),
        migrations.AlterField(
            model_name='source',
            name='numero',
            field=libretto.models.base.NumberCharField(blank=True, db_index=True, help_text='Sans «\xa0№\xa0». Exemple\u202f: «\xa052\xa0»', max_length=50, verbose_name='numéro'),
        ),
        migrations.RunPython(update_oeuvre_numero_extrait),
        CreateTreeTrigger('oeuvre', parent_field='extrait_de'),
        RebuildPaths('oeuvre'),
    ]