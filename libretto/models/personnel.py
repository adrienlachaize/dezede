# coding: utf-8

from __future__ import unicode_literals
import warnings
from django.db.models import (
    CharField, ForeignKey, ManyToManyField, permalink, SmallIntegerField,
    DateField, PositiveSmallIntegerField, Model, Q, get_model)
from django.template.defaultfilters import date
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.safestring import mark_safe
from django.utils.translation import (
    ungettext_lazy, ugettext_lazy as _, ugettext)
from common.utils.abbreviate import abbreviate
from common.utils.html import capfirst, href, date_html, sc
from common.utils.text import str_list
from .base import (CommonModel, LOWER_MSG, PLURAL_MSG, calc_pluriel,
                   UniqueSlugModel, AutoriteModel)
from .evenement import Evenement


__all__ = (
    b'Profession', b'Membre', b'TypeDEnsemble', b'Ensemble')


# TODO: Songer à l’arrivée des Emplois.
@python_2_unicode_compatible
class Profession(AutoriteModel, UniqueSlugModel):
    nom = CharField(_('nom'), max_length=200, help_text=LOWER_MSG, unique=True,
                    db_index=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
                            help_text=PLURAL_MSG)
    nom_feminin = CharField(
        _('nom (au féminin)'), max_length=230, blank=True,
        help_text=_('Ne préciser que s’il est différent du nom.'))
    parent = ForeignKey('self', blank=True, null=True,
                        related_name='enfants', verbose_name=_('parent'))
    classement = SmallIntegerField(default=1, db_index=True)

    class Meta(object):
        verbose_name = ungettext_lazy('profession', 'professions', 1)
        verbose_name_plural = ungettext_lazy('profession', 'professions', 2)
        ordering = ('classement', 'nom')
        app_label = 'libretto'
        permissions = (('can_change_status', _('Peut changer l’état')),)

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        relations = ('auteurs', 'elements_de_distribution',)
        if all_relations:
            relations += ('enfants', 'individus', 'parties', 'engagements',)
        return relations

    @permalink
    def get_absolute_url(self):
        return b'profession_detail', (self.slug,)

    @permalink
    def permalien(self):
        return b'profession_permanent_detail', (self.pk,)

    def pretty_link(self):
        return self.html(caps=True)

    def link(self):
        return self.html()

    def short_link(self):
        return self.short_html()

    def pluriel(self):
        return calc_pluriel(self)

    def feminin(self):
        f = self.nom_feminin
        return f or self.nom

    def html(self, tags=True, short=False, caps=False, feminin=False,
             pluriel=False):
        if pluriel:
            nom = self.pluriel()
            if feminin:
                warnings.warn("Pas de feminin pluriel pour l'instant")
        elif feminin:
            nom = self.feminin()
        else:
            nom = self.nom
        if caps:
            nom = capfirst(nom)
        if short:
            nom = abbreviate(nom, min_vowels=1, min_len=4, tags=tags)
        url = '' if not tags else self.get_absolute_url()
        out = href(url, nom, tags)
        return out

    def short_html(self, tags=True, pluriel=False):
        return self.html(tags, short=True, pluriel=pluriel)

    def __hash__(self):
        return hash(self.nom)

    def __str__(self):
        return capfirst(self.html(tags=False))

    def individus_count(self):
        return self.individus.count()
    individus_count.short_description = _('nombre d’individus')

    def oeuvres_count(self):
        return self.auteurs.oeuvres().count()
    oeuvres_count.short_description = _('nombre d’œuvres')

    def get_children(self):
        return self.enfants.all()

    def is_leaf_node(self):
        return not self.enfants.exists()

    @staticmethod
    def autocomplete_search_fields():
        return 'nom__icontains', 'nom_pluriel__icontains',


class PeriodeDActivite(Model):
    YEAR = 0
    MONTH = 1
    DAY = 2
    PRECISIONS = (
        (YEAR, _('Année')),
        (MONTH, _('Mois')),
        (DAY, _('Jour')),
    )
    debut = DateField(_('début'), blank=True, null=True)
    debut_precision = PositiveSmallIntegerField(
        _('précision du début'), choices=PRECISIONS, default=0)
    fin = DateField(_('fin'), blank=True, null=True)
    fin_precision = PositiveSmallIntegerField(
        _('précision de la fin'), choices=PRECISIONS, default=0)

    class Meta(object):
        abstract = True

    def _smart_date(self, attr, attr_precision, tags=True):
        d = getattr(self, attr)
        if d is None:
            return
        precision = getattr(self, attr_precision)
        if precision == self.YEAR:
            return force_text(d.year)
        if precision == self.MONTH:
            return date(d, 'F Y')
        if precision == self.DAY:
            return date_html(d, tags=tags)

    def smart_debut(self, tags=True):
        return self._smart_date('debut', 'debut_precision', tags=tags)

    def smart_fin(self, tags=True):
        return self._smart_date('fin', 'fin_precision', tags=tags)

    def smart_period(self, tags=True):
        debut = self.smart_debut(tags=tags)
        fin = self.smart_fin(tags=tags)
        # TODO: Rendre ceci plus simple en conservant les possibilités
        # d’internationalisation.
        if fin is None:
            if debut is None:
                return ''
            if self.debut_precision == self.DAY:
                t = ugettext('depuis le %(debut)s')
            else:
                t = ugettext('depuis %(debut)s')
        else:
            if debut is None:
                if self.fin_precision == self.DAY:
                    t = ugettext('jusqu’au %(fin)s')
                else:
                    t = ugettext('jusqu’à %(fin)s')
            else:
                if self.debut_precision == self.DAY:
                    if self.fin_precision == self.DAY:
                        t = ugettext('du %(debut)s au %(fin)s')
                    else:
                        t = ugettext('du %(debut)s à %(fin)s')
                else:
                    if self.fin_precision == self.DAY:
                        t = ugettext('de %(debut)s au %(fin)s')
                    else:
                        t = ugettext('de %(debut)s à %(fin)s')
        return t % {'debut': debut, 'fin': fin}
    smart_period.short_description = _('Période d’activité')


def limit_choices_to_instruments():
    return {'type': get_model('libretto', 'Partie').INSTRUMENT}


@python_2_unicode_compatible
class Membre(CommonModel, PeriodeDActivite):
    ensemble = ForeignKey('Ensemble', related_name='membres',
                          verbose_name=_('ensemble'))
    # TODO: Ajouter nombre pour les membres d'orchestre pouvant être saisi
    # au lieu d'un individu.
    individu = ForeignKey('Individu', related_name='membres',
                          verbose_name=_('individu'))
    instrument = ForeignKey(
        'Partie', blank=True, null=True, related_name='membres',
        limit_choices_to=limit_choices_to_instruments,
        verbose_name=_('instrument'))
    classement = SmallIntegerField(default=1)

    class Meta(object):
        verbose_name = _('membre')
        verbose_name_plural = _('membres')
        ordering = ('instrument', 'classement')
        app_label = 'libretto'

    def html(self, tags=True):
        l = [self.individu.html(tags=tags)]
        if self.instrument:
            l.append('[%s]' % self.instrument.html(tags=tags))
        if self.debut or self.fin:
            l.append('(%s)' % self.smart_period(tags=tags))
        return mark_safe(' '.join(l))

    def __str__(self):
        return self.html(tags=False)

    def link(self):
        return self.html()


@python_2_unicode_compatible
class TypeDEnsemble(CommonModel):
    nom = CharField(_('nom'), max_length=30, help_text=LOWER_MSG)
    nom_pluriel = CharField(_('nom pluriel'), max_length=30, blank=True,
                            help_text=PLURAL_MSG)
    parent = ForeignKey('self', null=True, blank=True,
                        related_name='enfants', verbose_name=_('parent'))

    class Meta(object):
        verbose_name = ungettext_lazy('type d’ensemble', 'types d’ensemble', 1)
        verbose_name_plural = ungettext_lazy('type d’ensemble',
                                             'types d’ensemble', 2)
        ordering = ('nom',)
        app_label = 'libretto'

    def __str__(self):
        return self.nom


@python_2_unicode_compatible
class Ensemble(AutoriteModel, PeriodeDActivite, UniqueSlugModel):
    particule_nom = CharField(
        _('particule du nom'), max_length=5, blank=True, db_index=True)
    nom = CharField(_('nom'), max_length=75, db_index=True)
    # FIXME: retirer null=True quand la base sera nettoyée.
    type = ForeignKey('TypeDEnsemble', null=True, related_name='ensembles')
    # TODO: Permettre deux villes sièges.
    siege = ForeignKey('Lieu', null=True, blank=True,
                       related_name='ensembles', verbose_name=_('siège'))
    # TODO: Ajouter historique d'ensemble.

    individus = ManyToManyField('Individu', through=Membre,
                                related_name='ensembles')

    class Meta(object):
        app_label = 'libretto'
        ordering = ('nom',)

    def __str__(self):
        return self.html(tags=False)

    def nom_complet(self):
        return ('%s %s' % (self.particule_nom, self.nom)).strip()

    def html(self, tags=True):
        nom = self.nom_complet()
        if tags:
            return href(self.get_absolute_url(),
                        sc(nom, tags=tags), tags=tags)
        return nom

    def link(self):
        return self.html()

    @permalink
    def get_absolute_url(self):
        return b'ensemble_detail', (self.slug,)

    @permalink
    def permalien(self):
        return b'ensemble_permanent_detail', (self.pk,)

    # TODO: Calculer les apparitions et les ajouter au template, comme pour
    #       les individus.

    def membres_html(self):
        return str_list([
            membre.html() for membre in
            self.membres.select_related('individu', 'instrument')])
    membres_html.short_description = _('membres')

    def membres_count(self):
        return self.membres.count()
    membres_count.short_description = _('nombre de membres')

    def apparitions(self):
        return Evenement.objects.filter(
            Q(distribution__ensemble=self)
            | Q(programme__distribution__ensemble=self)).distinct()

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('elements_de_distribution',)

    @staticmethod
    def autocomplete_search_fields():
        return ('particule_nom__icontains', 'nom__icontains',
                'siege__nom__icontains')
