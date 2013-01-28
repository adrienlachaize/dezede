# coding: utf-8

from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.test import Client, TransactionTestCase
from ...models import *
from datetime import date
from .utils import new, log_as_superuser


class LieuTestCase(TransactionTestCase):
    cleans_up_after_itself = True

    def setUp(self):
        theatre = new(NatureDeLieu, nom='théâtre')
        ville = new(NatureDeLieu, nom='ville')
        self.rouen = new(Lieu, nom='Rouen', nature=ville)
        self.theatre_des_arts = new(Lieu,
                                    nom='Théâtre des Arts', nature=theatre,
                                    parent=self.rouen)
        # Test client
        self.client = Client()
        log_as_superuser(self)

    def testComputedNames(self):
        self.assertEqual(unicode(self.rouen), 'Rouen')
        self.assertEqual(unicode(self.theatre_des_arts),
                         'Rouen, Théâtre des Arts')

    def testTemplateRenders(self):
        for oeuvre in [self.rouen, self.theatre_des_arts]:
            response = self.client.get(oeuvre.get_absolute_url())
            self.assertEqual(response.status_code, 200)

    def testAdminRenders(self):
        response = self.client.get(reverse('admin:catalogue_lieu_changelist'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('admin:catalogue_lieu_add'))
        self.assertEqual(response.status_code, 200)
        for lieu in [self.rouen, self.theatre_des_arts]:
            response = self.client.get(reverse('admin:catalogue_lieu_history',
                                               args=[lieu.pk]))
            self.assertEqual(response.status_code, 200)
            response = self.client.get(reverse('admin:catalogue_lieu_delete',
                                               args=[lieu.pk]))
            self.assertEqual(response.status_code, 200)
            response = self.client.get(reverse('admin:catalogue_lieu_change',
                                               args=[lieu.pk]))
            self.assertEqual(response.status_code, 200)


class SaisonTestCase(TransactionTestCase):
    cleans_up_after_itself = True

    def setUp(self):
        theatre = new(NatureDeLieu, nom='théâtre')
        ville = new(NatureDeLieu, nom='ville')
        rouen = new(Lieu, nom='Rouen', nature=ville)
        theatre_des_arts = new(Lieu,
            nom='Théâtre des Arts', nature=theatre, parent=rouen)
        self.saison = new(Saison,
            lieu=theatre_des_arts, debut=date(2011, 9, 1),
            fin=date(2012, 8, 31))
        # Test client
        self.client = Client()
        log_as_superuser(self)

    def testComputedNames(self):
        self.assertEqual(unicode(self.saison),
                         'Rouen, Théâtre des Arts, 2011–2012')

    def testAdminRenders(self):
        response = self.client.get(reverse('admin:catalogue_'
                                           'saison_changelist'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('admin:catalogue_saison_change',
                                      args=[self.saison.pk]))
        self.assertEqual(response.status_code, 200)