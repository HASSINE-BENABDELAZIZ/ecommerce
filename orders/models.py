from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from products.models import Product
from utils.s3 import PrivateMediaStorage
from io import BytesIO
from xhtml2pdf import pisa


def only_int(value):
    if not value.isdigit():
        raise ValidationError('is not correct')


STATUS_CHOICES = (
    ("AC", "ACTION REQUIRED"),
    ("NO", "NEW ORDER"),
    ("Co", "CONFIRMED"),
    ("Pr", "PRINTED"),
    ("Pa", "PACKED"),
    ("OS", "Shipped"),
    ("D", "COMPLETED"),
    ("F", "PROBLEMS"),
    ("awaiting_shipment", "Awaiting for shipment")
)
ORIGIN_CHOICES = (
    ("manual", "Manually added"),
    ("csv", "Imported from csv file"),
    ("shipstation", "Imported from Shipstation")

)
SUBSTATUS_CHOICES = (
    ("UC", "Uncategorized"),
    ("OC", "Out of stock"),
    ("PT", "PRE TRANSIT"),
    ("IT", "IN TRANSIT"),

)


class Cite(models.Model):
    name = models.CharField(max_length=255)
    ville_id = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Ville(models.Model):
    name = models.CharField(max_length=255)
    country_id = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Delegation(models.Model):
    pays_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Address(models.Model):
    company = models.CharField(
        max_length=255,
        verbose_name=_('Company'),
        blank=True,
        default=""
    )

    telephone = models.CharField(
        max_length=100,
        verbose_name=_('Telephone'),
        default="(619) 663-4134",
    )
    zipcode = models.CharField(
        max_length=15,
        verbose_name=_('Postal/Zip code')
    )

    cite = models.ForeignKey(
        Cite,
        default=None,
        blank=True,
        null=True,
        verbose_name="City",
        on_delete=models.SET_NULL)

    state = models.CharField(
        max_length=255,
        verbose_name=_('State/Province/Region'),
        blank=True
    )
    ville = models.ForeignKey(
        Ville,
        default=None,
        blank=True,
        null=True,
        verbose_name="Ville",
        on_delete=models.SET_NULL)
    deligation = models.ForeignKey(
        Delegation,
        default=None,
        blank=True,
        null=True,
        verbose_name="Delegation",
        on_delete=models.SET_NULL)
    address = models.CharField(max_length=255)

    @property
    def get_zipcode(self):
        return self.cite.zipcode if self.cite else self.zipcode

    @property
    def address_str(self):
        return "{}, {}, {}, {}".format(self.address, self.cite,
                                       self.state, self.zipcode, self.ville)

    def __str__(self):
        return "{}, {}, {}, {}".format(self.address, self.cite,
                                       self.state, self.zipcode, self.ville)


CARRIERS_CHOICES = [
    ("fp", "FP"),
    ("colissimo", "Colissimo"),
    ("beezit", "Beez it"),
    ("droppex", "Droppex"),
]


class Filliere(models.Model):
    name = models.CharField(max_length=255)
    address = models.ForeignKey(Address,
                                default=None,
                                blank=True,
                                null=True,
                                verbose_name="Address",
                                on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Carrier(models.Model):
    carrier = models.CharField(max_length=100, choices=CARRIERS_CHOICES, verbose_name="Transporteur")
    name = models.CharField(max_length=255, verbose_name='Nom')
    account_number = models.CharField(max_length=255, verbose_name="Numéro de compte")
    sender_address = models.ForeignKey(Address, verbose_name="Adresse de l'expéditeur", on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.carrier}{self.name}"


class FPCarrier(Carrier):
    username = models.CharField(max_length=100, verbose_name="FP Username")
    password = models.CharField(max_length=255, verbose_name="FP Password")

    def __str__(self):
        return self.username


class DroppexCarrier(Carrier):
    ENV_CHOICES = [
        ('dev', 'DEV'),
        ('prod', 'PROD')
    ]
    code_api = models.CharField(max_length=100, verbose_name="Code API")
    key_api = models.CharField(max_length=100, verbose_name="Clé API")


activity_type_choices = [
    ("in_transit", "in_transit"),
    ("exception", "exception"),
    ("delivery", "delivery"),
]


class Order(models.Model):
    SERVICE_CHOICES = [
        ('Livraison', 'LIVRAISON'),
        ('Echange', 'ECHANGE')
    ]
    order_number = models.CharField(verbose_name='order number', max_length=255, null=True, blank=True, unique=True)
    barcode_filename = models.CharField(max_length=255, blank=True)
    marketplace = models.ForeignKey("marketplace.Marketplace", null=True, blank=True, on_delete=models.SET_NULL)
    customer_name = models.CharField(verbose_name='Customer Name', max_length=255, null=True)
    customer_email = models.EmailField(verbose_name='Customer email', max_length=255, null=True, blank=True)
    company = models.CharField(verbose_name='Company', max_length=255, blank=True, null=True)
    livreur = models.ForeignKey(Carrier, default=None, blank=True, null=True, verbose_name="livreur",
                                on_delete=models.SET_NULL)
    client_ville = models.ForeignKey(Ville, default=None, blank=False, null=True, verbose_name="Ville",
                                     on_delete=models.SET_NULL)
    client_cite = models.ForeignKey(Cite, default=None, blank=False, null=True, verbose_name="Cite",
                                    on_delete=models.SET_NULL)
    client_deligaiton = models.ForeignKey(Delegation, default=None, blank=False, null=True, verbose_name="Delegation",
                                          on_delete=models.SET_NULL)
    client_zipcode = models.CharField(max_length=255, null=True, blank=True)
    expiditeur_ville = models.ForeignKey(Ville, default=None, blank=True, null=True, related_name="Exp_Ville",
                                         on_delete=models.SET_NULL)
    expiditeur_cite = models.ForeignKey(Cite, default=None, blank=True, null=True, related_name="Exp_Cite",
                                        on_delete=models.SET_NULL)
    expiditeur_deligaiton = models.ForeignKey(Delegation, default=None, blank=True, null=True,
                                              related_name="Exp_Delegation", on_delete=models.SET_NULL)
    expiditeur_zipcode = models.CharField(max_length=255, null=True, blank=True)
    client_address = models.CharField(max_length=255)
    phone = models.CharField(verbose_name='Phone', max_length=255, null=True)
    status = models.CharField(choices=STATUS_CHOICES, verbose_name='status', max_length=255, default="NO", blank=True,
                              null=True)
    substatus = models.CharField(choices=SUBSTATUS_CHOICES, verbose_name='status', max_length=255, default="",
                                 blank=True, null=True)
    tracking_code = models.CharField(verbose_name='Tracking code', max_length=255, default="", blank=True, null=True)
    estimated_shipment_cost = models.FloatField(default=0, blank=True, null=True)
    label = models.FileField(upload_to='order_label', storage=PrivateMediaStorage(), default=None, blank=True,
                             null=True)
    origin = models.CharField(choices=ORIGIN_CHOICES, verbose_name='origin', max_length=255, default="manual",
                              blank=True, null=True)
    note = models.TextField(null=True, blank=True)
    t_service = models.CharField(choices=SERVICE_CHOICES, max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    @property
    def total_price(self):
        items = self.children.all()
        count = 0
        for item in items:
            try:
                count += item.original_product.price * item.quantity
            except Exception:
                count += 0
        return count

    @property
    def total_weight(self):
        items = self.children.all()
        count = 0
        for item in items:
            try:
                count += item.original_product.weight
            except Exception:
                count += 0

        return count


    @property
    def shipment_cost(self):
        val = 0
        if self.total_weight < 10:
            val += self.marketplace.low_delivery if self.marketplace and self.marketplace.low_delivery else 8
        elif self.total_weight > 10:
            val += self.marketplace.high_delivery if self.marketplace and self.marketplace.high_delivery else 10

        return val



    @property
    def total(self):
        return self.total_price + self.shipment_cost
    @property
    def code_partenaire(self):
            return "1010101001"
    @property
    def nom_partenaire(self):
            return "Mylerz"

    def __str__(self):
        return f'STORELINKERS-{self.id}-{self.order_number}'
    def total_sans_tva(self):
        return self.total * 0.81


class OrderNotes(models.Model):
    note = models.TextField(default="", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.id)


def validate_number(value):
    if value == 0:
        raise ValidationError(
            _("is equal to 0"),
            params={'value': value},
        )


class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='children')
    original_order_item_id = models.IntegerField(default=None,
                                                 blank=True,
                                                 null=True)
    original_product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True,
                                         null=True)
    sku = models.CharField(max_length=255,
                           default=None,
                           null=True)
    name = models.CharField(max_length=255,
                            null=True)
    quantity = models.PositiveIntegerField(validators=[validate_number],
                                           default=1)

    def __str__(self):
        return str(self.name) + " " + str(self.id)


class OrderImports(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=255, default=None, null=True)
    file = models.FileField(upload_to='csv_files',
                            default=None,
                            storage=PrivateMediaStorage(),
                            )
    created_at = models.DateTimeField(auto_now_add=True,
                                      blank=True,
                                      null=True)
    finished_at = models.DateTimeField(auto_now_add=True,
                                       blank=True,
                                       null=True)

    @property
    def duration(self):
        return (self.finished_at - self.created_at).total_seconds()

    @property
    def file_url(self):
        if self.file:
            return self.file.url
        return "None"


class Shipment(models.Model):
    tracking_code = models.CharField(
        max_length=250,
        blank=True,
        default=None,
        null=True,
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True)
    label = models.FileField(
        default=None,
        blank=True,
        null=True,
        storage=PrivateMediaStorage()
    )
    carrier = models.ForeignKey(Carrier,
                                on_delete=models.CASCADE,
                                default=None,
                                blank=True,
                                null=True)

    @property
    def label_url(self):
        if self.label:
            return self.label.url
        return ""


class TrackingActivities(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    happened_at = models.DateTimeField(blank=True)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(blank=True, null=True, max_length=255)
    activity_type = models.CharField(max_length=100, choices=activity_type_choices)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    event_id = models.IntegerField(null=True, blank=True)


try:
    state_list = sorted(set((order.state, order.state) for order in Order.objects.order_by("state")))
except Exception:
    state_list = sorted(set())


class OrderExportFilters(models.Model):
    order_status = models.CharField(choices=STATUS_CHOICES,
                                    verbose_name='order status',
                                    max_length=255,
                                    blank=True,
                                    null=True)
    carrier = models.ForeignKey(Carrier,
                                on_delete=models.CASCADE,
                                default=None,
                                blank=True,
                                null=True)
    creation_date_start = models.DateTimeField(
        null=True)
    creation_date_finish = models.DateTimeField(
        null=True)
    state = models.CharField(choices=state_list,
                             verbose_name='State',
                             max_length=60,
                             null=True,
                             blank=True)

    class Meta:
        permissions = (('export-order', "export_order"),)


class OrderExportFiles(models.Model):
    progress = models.JSONField(null=True, blank=True)
    task_id = models.CharField(null=True,
                               blank=True,
                               max_length=200)
    line_number = models.IntegerField(null=True,
                                      blank=True,
                                      default=0)

    filters = models.ForeignKey(OrderExportFilters,
                                on_delete=models.CASCADE,
                                null=True,
                                blank=True)
    file = models.FileField(upload_to='excel',
                            storage=PrivateMediaStorage(),
                            default=None,
                            blank=True,
                            null=True
                            )

    created_at = models.DateTimeField(auto_now_add=True,
                                      blank=True)
    started_at = models.DateTimeField(blank=True,
                                      null=True)
    finished_at = models.DateTimeField(blank=True,
                                       null=True)

    status = models.CharField(verbose_name='status',
                              max_length=255,
                              blank=True,
                              null=True)

    percentage = models.FloatField(null=True, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             null=True,
                             blank=True)

    @property
    def duration(self):
        try:
            return (self.finished_at - self.started_at).total_seconds()
        except Exception:
            return 0

    @property
    def file_url(self):
        if self.file:
            return self.file.url
        return "None"


# Create your models here.
class PDFDocument(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

    def generate_pdf(self):
        # HTML content for the PDF
        html_content = f"""
        <html>
            <head>
                <title>{self.title}</title>
            </head>
            <body>
                <h1>{self.title}</h1>
                <p>{self.content}</p>
            </body>
        </html>
        """
        result = BytesIO()
        pdf = pisa.CreatePDF(html_content, dest=result)

        # Check if PDF generation was successful
        if not pdf.err:
            return result.getvalue()

        return None