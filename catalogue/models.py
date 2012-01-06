# coding: utf-8
from django.db.models import *
from tinymce.models import HTMLField
from django.template.defaultfilters import slugify
from filebrowser.fields import FileBrowseField

PLURAL_MSG = 'À remplir si le pluriel n\'est pas un simple ajout de « s ».  Exemple : « animal » devient « animaux » et non « animals ».'

def autoslugify(Mod, nom, slug):
    if slug != '':
        return slug
    nom_slug = slug_orig = slugify(nom)
    n = 0
    while Mod.objects.filter(slug=nom_slug).count():
        n += 1;
        nom_slug = slug_orig + str(n)
    return nom_slug

class Document(Model):
    nom = CharField(max_length=300, blank=True)
    document = FileBrowseField('Document', max_length=400, directory='documents/')
    description = HTMLField(blank=True)
    class Meta:
        ordering = ['document']
    def __unicode__(self):
        if self.nom:
            return self.nom
        return self.document.__unicode__()

class Illustration(Model):
    legende = CharField(max_length=300, blank=True, verbose_name='légende')
    image = FileBrowseField('Image', max_length=400, directory='images/')
    commentaire = HTMLField(blank=True)
    class Meta:
        ordering = ['image']
    def __unicode__(self):
        if self.nom:
            return self.nom
        return self.image.__unicode__()

class Etat(Model):
    nom = CharField(max_length=200)
    nom_pluriel = CharField(max_length=230, blank=True,
                            verbose_name='nom (au pluriel)',
                            help_text=PLURAL_MSG)
    message = CharField(max_length=300, blank=True,
                        help_text='Message à afficher dans la partie consultation.')
    slug = SlugField(blank=True)
    class Meta:
        verbose_name = 'état'
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Etat, self.nom, self.slug)
        super(Etat, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.nom

class NaturedeLieu(Model):
    nom = CharField(max_length=400)
    nom_pluriel = CharField(max_length=430, blank=True,
                            verbose_name='nom (au pluriel)',
                            help_text=PLURAL_MSG)
    slug = SlugField(blank=True)
    class Meta:
        verbose_name = 'nature de lieu'
        verbose_name_plural = 'natures de lieu'
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(NaturedeLieu, self.nom, self.slug)
        super(NaturedeLieu, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.nom

class Lieu(Model):
    nom = CharField(max_length=200)
    parent = ForeignKey('Lieu', related_name='enfants', null=True, blank=True)
    nature = ForeignKey(NaturedeLieu, related_name='lieux')
    historique = HTMLField(blank=True)
    illustrations = ManyToManyField(Illustration, related_name='lieux', blank=True, null=True)
    documents = ManyToManyField(Document, related_name='lieux', blank=True, null=True)
    etat = ForeignKey(Etat, related_name='lieux', null=True, blank=True)
    notes = HTMLField(blank=True)
    slug = SlugField(blank=True)
    class Meta:
        verbose_name_plural = 'lieux'
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Lieu, self.nom, self.slug)
        super(Lieu, self).save(*args, **kwargs)
    def __unicode__(self):
        if self.parent:
            return self.nom + ', ' + self.parent.nom
        return self.nom

class Saison(Model):
    lieu = ForeignKey(Lieu, related_name='saisons')
    debut = DateField(verbose_name='début')
    fin = DateField()
    class Meta:
        ordering = ['lieu', 'debut']
    def __unicode__(self):
        return self.lieu.__unicode__() + ', ' + self.debut.year.__str__() + '-' + self.fin.year.__str__()

class Profession(Model):
    nom = CharField(max_length=200)
    nom_pluriel = CharField(max_length=230, blank=True,
                            verbose_name='nom (au pluriel)',
                            help_text=PLURAL_MSG)
    parente = ForeignKey('Profession', blank=True, null=True, related_name='enfant')
    slug = SlugField(blank=True)
    class Meta:
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Profession, self.__unicode__(), self.slug)
        super(Profession, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.nom

class Individu(Model):
    nom = CharField(max_length=200)
    nom_naissance = CharField(max_length=200, verbose_name='nom de naissance', blank=True)
    prenoms = CharField(max_length=200, verbose_name='prénoms', blank=True)
    pseudonyme = CharField(max_length=200, blank=True)
    date_naissance = DateField(blank=True, null=True, verbose_name='date de naissance')
    lieu_naissance = ForeignKey(Lieu, related_name='individus_nes', blank=True, null=True, verbose_name='lieu de naissance')
    date_naissance_approx = CharField(max_length=200, blank=True,
                                      verbose_name='date approximative de naissance',
                                      help_text='Ne remplir que si la date de naissance est imprécise.')
    lieu_naissance_approx = CharField(max_length=200, blank=True,
                                      verbose_name='lieu approximatif de naissance',
                                      help_text='Ne remplir que si le lieu de naissance est imprécis.')
    date_mort = DateField(blank=True, null=True, verbose_name='date de décès')
    lieu_mort = ForeignKey(Lieu, related_name='individus_morts', blank=True, null=True, verbose_name='lieu de décès')
    date_mort_approx = CharField(max_length=200, blank=True,
                                 verbose_name='date approximative de décès',
                                 help_text='Ne remplir que si la date de décès est imprécise.')
    lieu_mort_approx = CharField(max_length=200, blank=True,
                                 verbose_name='lieu approximatif de décès',
                                 help_text='Ne remplir que si le lieu de décès est imprécis.')
    epoque = CharField(max_length=200, blank=True,
                       verbose_name='époque approximative',
                       help_text='Ne remplir que si aucun champ de date ci-dessus ne convient.')
    lieu_approx = CharField(max_length=200, blank=True,
                            verbose_name='lieu approximatif',
                            help_text='Ne remplir que si aucun champ de lieu ci-dessus ne convient.')
    professions = ManyToManyField(Profession, related_name='individus')
    parents = ManyToManyField('Individu', related_name='enfants', blank=True)
    biographie = HTMLField(blank=True)
    illustrations = ManyToManyField(Illustration, related_name='individus', blank=True, null=True)
    documents = ManyToManyField(Document, related_name='individus', blank=True, null=True)
    etat = ForeignKey(Etat, related_name='individus', null=True, blank=True)
    notes = HTMLField(blank=True)
    slug = SlugField(blank=True)
    class Meta:
        ordering = ['nom']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Individu, self.__unicode__(), self.slug)
        super(Individu, self).save(*args, **kwargs)
    def __unicode__(self):
        out = self.nom
        if self.prenoms:
            out = self.prenoms + ' ' + out
        if self.pseudonyme:
            out += ', dit ' + self.pseudonyme
        return out

class Devise(Model):
    nom = CharField(max_length=200, blank=True)
    symbole = CharField(max_length=10)

class Engagement(Model):
    individus = ManyToManyField(Individu, related_name='engagements')
    fonction = ForeignKey(Profession, related_name='engagements')
    salaire = FloatField(blank=True)
    devise = ForeignKey(Devise, blank=True, null=True, related_name='engagements')

class Personnel(Model):
    saison = ForeignKey(Saison, related_name='personnels')
    engagements = ManyToManyField(Engagement, related_name='personnels')

class NaturedOeuvre(Model):
    nom = CharField(max_length=400)
    nom_pluriel = CharField(max_length=430, blank=True,
                            verbose_name='nom (au pluriel)',
                            help_text=PLURAL_MSG)
    slug = SlugField(blank=True)
    class Meta:
        verbose_name="nature d'œuvre"
        verbose_name_plural="natures d'œuvre"
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(NaturedOeuvre, self.nom, self.slug)
        super(NaturedOeuvre, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.nom

class Role(Model):
    nom = CharField(max_length=200)
    importance = FloatField()
    class Meta:
        verbose_name = 'rôle'
        ordering = ['importance']
    def __unicode__(self):
        return self.nom

class Pupitre(Model):
    role = ForeignKey(Role, related_name='pupitres', verbose_name='rôle')
    quantite_min = IntegerField(default=1, verbose_name='quantité minimale')
    quantite_max = IntegerField(default=1, verbose_name='quantité maximale')
    def __unicode__(self):
        out = str(self.quantite_min)
        if self.quantite_min != self.quantite_max:
            out += ' à %d' % self.quantite_max
        out += self.role
        return out

class Oeuvre(Model):
    prefixe = CharField(max_length=20, blank=True, verbose_name='préfixe')
    titre = CharField(max_length=200)
    soustitre = CharField(max_length=200, blank=True, verbose_name='sous-titre')
    nature = ForeignKey(NaturedOeuvre, related_name='oeuvres')
    caracteristique = CharField(max_length=400, verbose_name='caractéristique', blank=True)
    auteurs = ManyToManyField(Individu, related_name='oeuvres', blank=True, null=True)
    description = HTMLField(blank=True)
    pupitres = ManyToManyField(Role, related_name='oeuvres', blank=True, null=True)
    parents = ManyToManyField('Oeuvre', related_name='enfants', blank=True, null=True)
    referenced = BooleanField(default=True, verbose_name='référencée')
    documents = ManyToManyField(Document, related_name='oeuvres', blank=True, null=True)
    illustrations = ManyToManyField(Illustration, related_name='oeuvres', blank=True, null=True)
    etat = ForeignKey(Etat, related_name='oeuvres', null=True, blank=True)
    notes = HTMLField(blank=True)
    slug = SlugField(blank=True)
    class Meta:
        verbose_name = 'œuvre'
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(Oeuvre, self.titre, self.slug)
        super(Oeuvre, self).save(*args, **kwargs)
    def __unicode__(self):
        if self.soustitre and Oeuvre.objects.filter(titre=self.titre).count() > 1:
            return self.titre + ' / ' + self.soustitre
        else:
            return self.titre

class AttributiondeRole(Model):
    pupitre = ForeignKey(Pupitre, related_name='attributions_de_role')
    individus = ManyToManyField(Individu, related_name='attributions_de_role')
    class Meta:
        verbose_name = 'attribution de rôle'
    def __unicode__(self):
        return self.pupitre

class ElementdeProgramme(Model):
    oeuvre = ForeignKey(Oeuvre, related_name='elements_de_programme', verbose_name='œuvre', blank=True, null=True)
    autre = HTMLField(blank=True)
    premiere_relative = BooleanField(verbose_name='première relative')
    premiere_absolue = BooleanField(verbose_name='première absolue')
    classement = FloatField()
    distribution = ManyToManyField(AttributiondeRole, related_name='elements_de_programme', blank=True, null=True)
    illustrations = ManyToManyField(Illustration, related_name='representations', blank=True, null=True)
    documents = ManyToManyField(Document, related_name='representations', blank=True, null=True)
    etat = ForeignKey(Etat, related_name='elements_de_programme', null=True, blank=True)
    class Meta:
        verbose_name = 'élément de programme'
        verbose_name_plural = 'éléments de programme'
        ordering = ['classement']
    def __unicode__(self):
        return self.oeuvre

class Evenement(Model):
    date_debut = DateField()
    heure_debut = TimeField(blank=True, null=True)
    date_fin = DateField(blank=True, null=True, help_text='À ne préciser que si l\'événement dure plusieurs jours.')
    heure_fin = TimeField(blank=True, null=True)
    lieu = ForeignKey(Lieu, related_name='evenements')
    relache = BooleanField(verbose_name='relâche')
    circonstance = CharField(max_length=500, blank=True)
    programme = ManyToManyField(ElementdeProgramme, related_name='evenements', blank=True, null=True)
    documents = ManyToManyField(Document, related_name='evenements', blank=True, null=True)
    illustrations = ManyToManyField(Illustration, related_name='evenements', blank=True, null=True)
    etat = ForeignKey(Etat, related_name='evenements', null=True, blank=True)
    notes = HTMLField(blank=True)
    class Meta:
        verbose_name = 'événement'
        ordering = ['date_debut', 'heure_debut', 'lieu']
    def __unicode__(self):
        return self.lieu.nom + ' le ' + self.date_debut.__str__()

class TypedeSource(Model):
    nom = CharField(max_length=200)
    nom_pluriel = CharField(max_length=230, blank=True,
                            verbose_name='nom (au pluriel)',
                            help_text=PLURAL_MSG)
    slug = SlugField(blank=True)
    class Meta:
        verbose_name = 'type de source'
        verbose_name_plural = 'types de source'
        ordering = ['slug']
    def save(self, *args, **kwargs):
        self.slug = autoslugify(TypedeSource, self.nom, self.slug)
        super(TypedeSource, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.nom

class Source(Model):
    nom = CharField(max_length=200)
    numero = CharField(max_length=50, blank=True)
    date = DateField()
    page = CharField(max_length=50, blank=True)
    type = ForeignKey(TypedeSource, related_name='sources')
    contenu = HTMLField(blank=True)
    evenements = ManyToManyField(Evenement, related_name='sources', blank=True, null=True)
    documents = ManyToManyField(Document, related_name='sources', blank=True, null=True)
    illustrations = ManyToManyField(Illustration, related_name='sources', blank=True, null=True)
    etat = ForeignKey(Etat, related_name='sources', null=True, blank=True)
    notes = HTMLField(blank=True)
    class Meta:
        ordering = ['date', 'nom']
    def __unicode__(self):
        return self.pk.__str__()

