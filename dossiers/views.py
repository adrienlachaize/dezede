# coding: utf-8

from __future__ import unicode_literals

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from accounts.models import HierarchicUser
from libretto.models import Source, Oeuvre
from libretto.views import (
    PublishedListView, PublishedDetailView, EvenementListView)
from .jobs import dossier_to_pdf
from .models import CategorieDeDossiers, DossierDEvenements
from .utils import launch_pdf_export


class CategorieDeDossiersList(PublishedListView):
    model = CategorieDeDossiers
    has_frontend_admin = False


class DossierDEvenementsDetail(PublishedDetailView):
    model = DossierDEvenements


class DossierDEvenementsDataDetail(EvenementListView):
    template_name = 'dossiers/dossierdevenements_data_detail.html'
    view_name = 'dossierdevenements_data_detail'
    enable_default_page = False

    def get_queryset(self):
        self.object = get_object_or_404(DossierDEvenements,
                                        pk=self.kwargs['pk'])
        if not self.object.can_be_viewed(self.request):
            raise PermissionDenied
        return super(DossierDEvenementsDataDetail, self).get_queryset(
            base_filter=Q(pk__in=self.object.get_queryset()))

    def get_context_data(self, **kwargs):
        data = super(DossierDEvenementsDataDetail, self) \
            .get_context_data(**kwargs)
        data['object'] = self.object
        return data

    def get_success_view(self):
        return self.view_name, int(self.kwargs['pk'])


class DossierDEvenementsDetailXeLaTeX(DossierDEvenementsDetail):
    def get_object(self, queryset=None):
        if not self.request.user.is_authenticated():
            raise PermissionDenied
        return super(DossierDEvenementsDetailXeLaTeX,
                     self).get_object(queryset)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        launch_pdf_export(dossier_to_pdf, request, self.object.pk,
                          'du dossier « %s »' % self.object)
        return redirect(reverse('dossierdevenements_detail',
                                args=(self.object.pk,)))


class OperaComiquePresentation(TemplateView):
    template_name = 'dossiers/opera_comique_presentation.html'

    def get_context_data(self, **kwargs):
        context = super(OperaComiquePresentation,
                        self).get_context_data(**kwargs)
        context['oc_user'] = HierarchicUser.objects.get(pk=103)
        return context


class OperaComiqueListView(PublishedListView):
    model = Source
    template_name = 'dossiers/opera_comique.html'

    def get_queryset(self):
        qs = super(OperaComiqueListView, self).get_queryset()
        return qs.filter(owner_id=103)

    def get_context_data(self, **kwargs):
        context = super(OperaComiqueListView, self).get_context_data(**kwargs)
        qs = context['object_list']
        oeuvres = (
            Oeuvre.objects.filter(sources__in=qs).distinct()
            .select_related('genre', 'creation_lieu', 'creation_lieu__nature')
            .prefetch_related('auteurs__individu', 'auteurs__profession',
                              'caracteristiques__type'))
        if self.request.GET.get('order_by') == 'creation_date':
            oeuvres = oeuvres.order_by('creation_date')
        else:
            oeuvres = oeuvres.order_by(*Oeuvre._meta.ordering)
        context['oeuvres'] = oeuvres
        return context
