from django.db import models
from django.templatetags.static import static


class Category(models.Model):
    name = models.CharField(max_length=80)

    class Meta:
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=80)

    class Meta:
        verbose_name_plural = "Sous Catégories"

    def __str__(self):
        return self.name


class Product(models.Model):
    sku = models.CharField(verbose_name='SKU', max_length=255, unique=True, blank=False, null=False)
    marketplace = models.ForeignKey("marketplace.Marketplace", on_delete=models.SET_NULL, null=True)
    name = models.CharField(verbose_name='Nom', max_length=255, blank=False, null=False)
    brand = models.CharField(verbose_name='Marque', max_length=255, blank=False, null=False)
    weight = models.FloatField(verbose_name='Poids', blank=False, null=False)
    year = models.IntegerField(verbose_name='Année', blank=True, null=False)
    price = models.FloatField(verbose_name='Prix', blank=False, null=False)
    currency = models.CharField(verbose_name='Devise', max_length=50, default='TND', null=False)
    stock = models.IntegerField(verbose_name='Quantité', blank=False, null=False)
    image_url = models.ImageField(verbose_name='Image', upload_to='products/', default=None, blank=False, null=False)
    upc = models.CharField(verbose_name='CUP', max_length=255, blank=False, null=False)
    status = models.BooleanField(verbose_name='Statut Actuel', default=True, blank=False, null=False)
    category = models.ForeignKey(Category, verbose_name='Catégorie', on_delete=models.SET_NULL,
                                 null=True)  # Change null=False to null=True
    subcategory = models.ForeignKey(SubCategory, verbose_name='Sous Catégorie', on_delete=models.SET_NULL, blank=True,
                                    null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=True)

    @property
    def image_path(self):
        if self.image_url:
            return self.image_url.url
        return static("images/default_product1.png")

    def __str__(self):
        return str(self.sku)
