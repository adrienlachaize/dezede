# coding: utf-8

from __future__ import unicode_literals
from django.conf.urls import patterns, url
from django.views.generic import RedirectView
from dossiers.views import (
    CategorieDeDossiersList, DossierDEvenementsDetail,
    DossierDEvenementsDataDetail, DossierDEvenementsDetailXeLaTeX,
    OperaComiquePresentation, OperaComiqueListView,
    DossierDEvenementsDataGeoJson)


urlpatterns = patterns('',
    url(r'^$', CategorieDeDossiersList.as_view(),
        name='dossierdevenements_index'),
    url(r'^62/?$', RedirectView.as_view(
        pattern_name='dossier_opera_comique_presentation', permanent=False)),
    url(r'^archives[-\.]opera-comique$', OperaComiquePresentation.as_view(),
        name='dossier_opera_comique_presentation'),
    url(r'^archives[-\.]opera-comique/data$', OperaComiqueListView.as_view(),
        name='dossier_opera_comique'),
    url(r'^(?P<pk>\d+)/$', DossierDEvenementsDetail.as_view(),
        name='dossierdevenements_detail'),
    url(r'^(?P<pk>\d+)/data$', DossierDEvenementsDataDetail.as_view(),
        name='dossierdevenements_data_detail'),
    url(r'^(?P<pk>\d+)/geojson$', DossierDEvenementsDataGeoJson.as_view(),
        name='dossierdevenements_data_geojson'),
    url(r'^(?P<pk>\d+)/export',
        DossierDEvenementsDetailXeLaTeX.as_view(),
        name='dossierdevenements_detail_xelatex'),
)
