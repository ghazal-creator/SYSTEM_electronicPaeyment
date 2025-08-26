from django.urls import path 
from .import views

urlpatterns = [
    
    path('userRegister/', views.userRegister, name='userRegister'),
    path('login/', views.userLogin, name='user_login'),
    path('forget-password/', views.forget_password, name='forget_password'),
    path('reset_Password/', views.reset_Password, name='reset_Password'),
    path('send-otp/', views.send_Otp, name='send_otp'),
    path('logout/', views.doLogout, name='logout'),
    path('wallet/', views.get_wallet_balance, name='wallet_balance'),
    path('transactions/latest/', views.get_latest_transactions, name='latest_transactions'),
    path('transactions/frequent-recipients/', views.get_frequent_recipients, name='frequent_recipients'),
    path('transactions/history/', views.get_transaction_history, name='transaction_history'),
    path('transactions/send/', views.send_transfer, name='send_transfer'),
    path('wallet/topup/', views.wallet_topup, name=' wallet_topup'),
    path('transactions/receive/', views.get_incoming_transfer, name='incoming_transfer'),
    path('BillPay/', views.PayBill, name='PayBill'),
    path('receipts/', views.get_receipts, name='get_receipts'),
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/mark-read/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('login-email/', views.login_with_email, name='login_with_email'),
    path('bills/paid/', views.get_paid_bills, name='get_paid_bills'),
    path('transactions/details/', views.get_transaction_details, name='transaction_details'), 
    path('transactions/paginated/', views.get_transactions_paginated, name='transactions_paginated'),
    path('transfers/', views.get_user_transfers, name='user_transfers'),
    path('UpdateRecipient/', views.update_recipient, name='update_recipient'),
    path('frequent-contacts/delete/', views.delete_frequent_contact, name='delete_frequent_contact'),
    path('frequent-contacts/', views.get_frequent_contacts, name='get_frequent_contacts'),
    path('analytics/balance-history/', views.GetBalanceHistory, name='balance_history'),
    path('analytics/spending-analysis/', views.GetSpendingAnalysis, name='spending_analysis'),
    path('user/preferences/', views.GetUserPreferences, name='get_user_preferences'),
    path('user/preferences/update/', views.update_user_preferences, name='update_user_preferences'),
]
 
