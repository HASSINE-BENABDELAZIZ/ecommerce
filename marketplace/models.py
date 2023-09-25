from datetime import timedelta

from django.db import models

from orders.models import Cite, Address, Delegation, Ville, Filliere, Carrier


class Secteur(models.Model):
    activiter = models.CharField(max_length=255)


SECTEUR_CHOICES = [
    ("produit bio", "produit bio"),
    ("textile", "textile"),
    ("Divers", "Divers"),
]


class Marketplace(models.Model):
    commercial = models.ForeignKey("accounts.User", default=None, blank=True, null=True, on_delete=models.SET_NULL,
                                   related_name="fournisseur_commercial")
    filiere = models.ForeignKey(Filliere, default=None, blank=True, null=True, verbose_name="filiere",
                                on_delete=models.SET_NULL)
    name = models.CharField(default=None, max_length=100)
    responsable = models.CharField(default=None, max_length=100)
    stock_service = models.BooleanField(default=False)
    phone = models.CharField(default=None, max_length=100)
    email = models.EmailField(max_length=300)
    ville = models.ForeignKey(Ville, default=None, blank=True, null=True, verbose_name="Ville",
                              on_delete=models.SET_NULL)
    delegation = models.ForeignKey(Delegation, default=None, blank=True, null=True, verbose_name="Delegation",
                                   on_delete=models.SET_NULL)
    address = models.CharField(max_length=255)
    cite = models.ForeignKey(Cite, default=None, blank=True, null=True, verbose_name="Cite", on_delete=models.SET_NULL)
    code_postale = models.IntegerField(null=True)
    img = models.ImageField(default=None, blank=True, null=True, upload_to='Fournisseurs/')
    rib = models.CharField(max_length=150, blank=True, null=True)
    mf = models.CharField(max_length=150, default=None, blank=True, null=True)
    secteur = models.ManyToManyField(Secteur, choices=SECTEUR_CHOICES, related_name='fournisseur_secteur')
    nb_order = models.IntegerField(default=0, null=True, blank=True)
    tentative = models.IntegerField(default=3, null=True, blank=True)
    low_delivery = models.FloatField(default=8, blank=True, null=True)
    low_return = models.FloatField(default=5, blank=True, null=True)
    high_delivery = models.FloatField(default=11, blank=True, null=True)
    high_return = models.FloatField(default=6, blank=True, null=True)

    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE, default=None, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def photo_url(self):
        if self.img:
            return self.img.url
        from django.templatetags.static import static

        return static("images/avatar_default.png")

    @property
    def get_only_date(self):
        return str(self.created_at.date()) + " à " + str((self.created_at + timedelta(hours=1)).strftime("%H:%M"))

    @property
    def absolute_address(self):
        return f"{self.adress} {self.ville}, {self.delegation}, {self.code_postale}"

    @property
    def secteur_names(self):
        names = []
        for i in self.secteur.all():
            names.append(i.activiter)
        return names

    def __str__(self):
        return f"{self.name} ({self.responsable})"


class FinanceMarketplace(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    marketplace = models.ForeignKey(Marketplace,
                                    default=None,
                                    blank=True,
                                    null=True,
                                    on_delete=models.SET_NULL)
    nombre_de_colis = models.IntegerField(default=0,
                                          blank=True,
                                          null=True)
    total_cod = models.FloatField(default=0,
                                  blank=True,
                                  null=True)
    total_hfl = models.FloatField(default=0,
                                  blank=True,
                                  null=True)
    cous_livraison = models.FloatField(default=0,
                                       blank=True,
                                       null=True)

    user_id = models.IntegerField(blank=True, null=True)

    @property
    def get_only_date(self):
        return str(self.created_at.date()) + " à " + str((self.created_at + timedelta(hours=1)).strftime("%H:%M"))

    @property
    def get_only_updated_date(self):
        return str(self.updated_at.date()) + " à " + str((self.updated_at + timedelta(hours=1)).strftime("%H:%M"))

    @property
    def fournisseur_name(self):
        return self.marketplace.name if self.marketplace else ""

    @property
    def fournisseur_number(self):
        return self.marketplace.tel if self.marketplace else 0

    @property
    def fournisseur_mf(self):
        return self.marketplace.mf if self.marketplace else ""

    def __str__(self):
        return f"{self.marketplace.name if self.marketplace else None} ({self.nombre_de_colis})"
