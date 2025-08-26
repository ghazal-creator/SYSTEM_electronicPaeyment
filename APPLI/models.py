from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
import uuid  


# Create your models here.
class User(models.Model):
    uuid = models.CharField(default=uuid.uuid4, editable=False, max_length=40, unique=True)
    name = models.CharField(max_length=100)
    user_name = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=128)
    Phone_NO = models.CharField(max_length=50, unique=True)
    age = models.IntegerField()
    image = models.ImageField(upload_to='User_images/',default='user/R.png')
    active = models.BooleanField(default=True)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_create_time = models.DateTimeField(null=True, blank=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def __str__(self):
        return self.name
class Institution(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Branch(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
class Admin(models.Model):
    uuid = models.CharField(default=uuid.uuid4, editable=False, max_length=40) 
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    branch = models.ForeignKey(Branch, related_name="admin", on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=4)
    
    def __str__(self):
        return self.name
class WalletType(models.Model):
    name = models.CharField(max_length=50, unique=True)  
    label = models.CharField(max_length=100)  
    description = models.TextField(blank=True)  
    max_balance = models.FloatField(null=True, blank=True)  
    is_active = models.BooleanField(default=True)  

    def str(self):
        return self.label

    class Meta:
        verbose_name = 'نوع المحفظة'
        verbose_name_plural = 'أنواع المحافظ'        

class Wallet(models.Model):
    uuid = models.CharField(default=uuid.uuid4, editable=False, max_length=40)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0.0)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    wallet_type = models.ForeignKey(WalletType,on_delete=models.CASCADE,null=True,blank=True)
  

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'wallet_type', 'currency'],
                name='unique_wallet_per_type_and_currency_per_user'
            )
        ]
class ServiceCategory(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)

class ServiceType(models.Model):
    name = models.CharField(max_length=100,default="other")
    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT)
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('send', 'Send'),
        ('receive', 'Receive'),
        ('topup', 'Top-Up'),
        ('bill', 'Bill Payment'),
    ]

    STATUS_CHOICES = [
        ('pending', 'معلقة'),
        ('completed', 'منتهية'),
        ('failed', 'فشلت'),
    ]
    recipient_name = models.CharField(max_length=100, null=True, blank=True)
    service_type =  models.ForeignKey(ServiceType,on_delete=models.SET_NULL, null=True, blank=True)
    reference_number = models.CharField("reference_number", max_length=50, unique=True)
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    sender = models.ForeignKey(User, related_name="sent_transactions", on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name="received_transactions", on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, null=True, blank=True)
    transfer_amount = models.DecimalField("transfer_amount", max_digits=12, decimal_places=2)
    payment_amount = models.DecimalField("payment_amount", max_digits=12, decimal_places=2)
    fee = models.DecimalField("fee", max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField("total_amount", max_digits=15, decimal_places=2)
    transaction_date = models.DateField("transaction_date")
    transaction_time = models.TimeField("transaction_time")
    status = models.CharField("status",max_length=20,choices=STATUS_CHOICES)
    subscription_number = models.CharField(max_length=50, blank=True, null=True)
   
class Payment(models.Model):
   
    
    transaction = models.OneToOneField(Transaction, related_name="payment", on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=20)
    currency = models.ForeignKey(Currency, related_name="payments", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    payment_time = models.TimeField()
class Receipt(models.Model):
    transaction = models.OneToOneField(Transaction, related_name="receipt", on_delete=models.CASCADE)
    pdf_file = models.FileField(upload_to="receipts/")
    created_at = models.DateTimeField(auto_now_add=True)
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255) 
    image = models.ImageField(upload_to='Notification_images/',default='Notification_images/OIP.jfif') 
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

class Notification_Transactions(models.Model):
    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateField(auto_now_add=True)
class AuditLog(models.Model):
    transaction = models.ForeignKey(Transaction, related_name="audit_logs", on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    performed_by = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    
class FrequentContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='frequent_contacts')
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    ccontact_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    

    class Meta:
        ordering = ['-last_used', '-created_at']
        unique_together = ['user', 'phone_number']

    def __str__(self):
        return f"{self.name} ({self.phone_number})"


class TransactionCategory(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=30)  

    def __str__(self):
        return self.name
class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preference')
    default_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    language = models.CharField(max_length=10, default='ar')  
    theme = models.CharField(max_length=20, default='light')  

    def __str__(self):
        return f"Preferences of {self.user.name}"
