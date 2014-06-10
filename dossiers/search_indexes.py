# coding: utf-8

from __future__ import unicode_literals, division
from haystack.indexes import Indexable, EdgeNgramField
from libretto.search_indexes import CommonSearchIndex
from .models import DossierDEvenements


class DossierDEvenementsIndex(CommonSearchIndex, Indexable):
    content_auto = EdgeNgramField(model_attr='titre')

    def get_model(self):
        return DossierDEvenements

    def prepare(self, obj):
        prepared_data = super(DossierDEvenementsIndex, self).prepare(obj)
        prepared_data['boost'] *= 5.0 / (obj.level + 1)
        return prepared_data