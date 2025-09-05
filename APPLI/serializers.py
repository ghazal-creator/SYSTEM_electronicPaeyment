from rest_framework import serializers
from .models import (
    User, Institution, Branch, Admin,
    Currency, WalletType, Wallet,
    ServiceCategory, ServiceType,
    Transaction, Payment, Receipt,
    Notification, Notification_Transactions,
    AuditLog, FrequentContact,
    TransactionCategory, UserPreference
)

# ----------------- User -----------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "uuid", "name", "user_name", "email",
            "Phone_NO", "age", "image", "active"
        ]


# ----------------- Institution / Branch / Admin -----------------
class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = "all"

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = "all"

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = "all"


# ----------------- Currency & Wallet -----------------
class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ["id", "code", "name", "exchange_rate"]

class WalletTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletType
        fields = "all"

class WalletSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer()
    wallet_type = WalletTypeSerializer()

    class Meta:
        model = Wallet
        fields = ["id", "uuid", "balance", "currency", "wallet_type"]


# ----------------- Services -----------------
class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = "all"

class ServiceTypeSerializer(serializers.ModelSerializer):
    category = ServiceCategorySerializer()

    class Meta:
        model = ServiceType
        fields = ["id", "name", "category"]


# ----------------- Transaction & Payment -----------------
class TransactionSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    recipient = UserSerializer()
    wallet = WalletSerializer()
    service_type = ServiceTypeSerializer()

    class Meta:
        model = Transaction
        fields = [
            "id", "reference_number", "transaction_type", "recipient_name",
            "sender", "recipient", "wallet", "service_type",
            "transfer_amount", "payment_amount", "fee", "total_amount",
            "transaction_date", "transaction_time", "status",
            "subscription_number"
        ]

class PaymentSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer()
    currency = CurrencySerializer()

    class Meta:
        model = Payment
        fields = [
            "id", "transaction", "payment_type", "currency",
            "amount", "payment_date", "payment_time"
        ]


# ----------------- Receipt -----------------
class ReceiptSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer()

    class Meta:
        model = Receipt
        fields = ["id", "transaction", "pdf_file", "created_at"]


# ----------------- Notifications -----------------
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "image", "created_at", "is_read"]

class NotificationTransactionSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer()

    class Meta:
        model = Notification_Transactions
        fields = ["id", "transaction", "message", "created_at"]


# ----------------- Audit Logs -----------------
class AuditLogSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer()

    class Meta:
        model = AuditLog
        fields = "all"
# ----------------- Frequent Contact -----------------
class FrequentContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrequentContact
        fields = ["id", "name", "phone_number", "ccontact_id", "created_at", "last_used"]


# ----------------- Transaction Category -----------------
class TransactionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionCategory
        fields = "all"


# ----------------- User Preferences -----------------
class UserPreferenceSerializer(serializers.ModelSerializer):
    default_currency = CurrencySerializer()

    class Meta:
        model = UserPreference
        fields = ["id", "default_currency", "language", "theme"]        