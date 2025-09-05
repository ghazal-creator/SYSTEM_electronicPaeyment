from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
import random
from .models import *
from django.core.exceptions import ObjectDoesNotExist  
from django.db.models import Sum, Q, Count 
from django.utils import timezone  
from decimal import Decimal  
import uuid  
from django.core.paginator import Paginator
from django.contrib.auth import authenticate  
from django.utils.dateparse import parse_date          
from django.http import JsonResponse
from datetime import timedelta
from django.views.decorators.http import require_http_methods
from django.db.models.functions import TruncMonth
import secrets
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect


ROOT_URL = "http://127.0.0.1:8000/"
@csrf_exempt
def userRegister(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)

        name = body_d['name']
        user_name = body_d['user_name']
        email = body_d['email']
        password = body_d['password']
        confirm_password = body_d['confirm_password']
        Phone_NO = body_d['Phone_NO']
        age = body_d['age']
        image = request.FILES.get('image')

        if password != confirm_password:
            return JsonResponse({'response': 'error', 'message': 'كلمة المرور غير متطابقة'})

        if User.objects.filter(user_name=user_name).exists():
            return JsonResponse({'response': 'error', 'data': 'الحساب موجود مسبقاً'})
        
        if image:
            User.image=image
        else:
            pass
        
        user = User(user_name=user_name, name=name, Phone_NO=Phone_NO, age=age, email=email )
        user.set_password(password)
        user.save()
        
        default_currency = Currency.objects.get(code='USD')  
        Wallet.objects.create(user=user, balance=0.0, currency=default_currency)

        return JsonResponse({'response': 'ok'})

    except Exception as e:
        print(e)
        return JsonResponse({'response': 'error', 'message': str(e)})
@csrf_exempt
def userLogin(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)
        Phone_NO = body_d['Phone_NO']
        password = body_d['password']

        user = User.objects.filter(Phone_NO=Phone_NO).first() 
        if user and user.check_password(password):  
            d = {
                'id': user.id,
                'name': user.name,
                'user_name': user.user_name,
                'Phone_NO': user.Phone_NO,
                'age': user.age
            }
            return JsonResponse({'response': 'ok', 'data': d})
        else:
            return JsonResponse({'response': 'error', 'message': 'Incorrect phone number or password'})
    except Exception as e:
        print(e)
        return JsonResponse({'response': 'error', 'message': 'حدث خطأ في الخادم'})
@csrf_exempt
def forget_password(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)
        email = body_d['email']
        Phone_NO = body_d['Phone_NO']
        if not email and not phone_no:
            return JsonResponse({'response': 'error','message': 'Please enter your phone number or email'}, status=400)
        
        try:
            user = User.objects.get(email=email, Phone_NO=Phone_NO)  
        except User.DoesNotExist:  
            return JsonResponse({'response': 'error','message': 'This account does not exist'},status=404)   
            otp =str(secrets.randbelow(900000) + 100000)
            user.otp_code = otp
            user.otp_create_time = timezone.now()
            user.save()
           
            print(f"OTP for {user.email or user.Phone_NO}: {otp}")
        return JsonResponse({'response': 'ok', 'message': f' OTP: {otp} '})
    except Exception as e:
        print(e)
        return JsonResponse({'response': 'error', 'message': 'Internal server error'}, status=500)

@csrf_exempt
def send_Otp(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)
        U_ID = body_d['U_ID']
        Phone_NO = body_d['Phone_NO']
        if not U_ID or not Phone_NO : 
           return JsonResponse({"status": "error","message": "Missing user ID or phone number"}, status=400)
        try:
            u = User.objects.get(id=U_ID)
            if u.Phone_NO != Phone_NO :
               u.Phone_NO = Phone_NO 
               otp = str(secrets.randbelow(900000) + 100000)
            user.otp_code = otp
            user.otp_create_time = timezone.now()
            user.save()
            
            print(f"OTP for user {U_ID}: {otp}")
            u.save()
            return JsonResponse({"result": "OTP sent successfully",  "otp": otp})
        except Exception as e:
            print(e)
            return JsonResponse({  "result": "error",
                "message": "User not found"
            }, status=404)
    except Exception as e:
        print(e)
        return JsonResponse({"result": "error",
            "message": "Internal server error"
        }, status=500)
@csrf_exempt
def verify_otp(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)
        U_ID = body_d['U_ID']        
        otp_code = body_d['otp_code']
        user = User.objects.get(id=U_ID)
        if (timezone.now() - user.otp_create_time).total_seconds() > 300:
            new_otp = str(secrets.randbelow(900000) + 100000)
            user.otp_code = new_otp
            user.otp_create_time = timezone.now()
            user.save()          
            return JsonResponse({'status': 'expired','message': 'OTP expired. New OTPgenerated','new_otp': new_otp}, status=400)
            if user.otp_code != otp_code:
               return JsonResponse({'status': 'error','message': 'Invalid OTP'}, status=401)
        return JsonResponse({'status': 'success','message': 'OTP verified successfully'}, status=200)
    except KeyError as e:
        return JsonResponse({'status': 'error','message': f'Missing field: {str(e)}'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error','message': 'User not found'}, status=404)
    except Exception as e:
        print(f"Server Error: {str(e)}")
        return JsonResponse({'status': 'error','message': 'Internal server error'}, status=500)        
@csrf_exempt
def reset_Password(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)
        U_ID = body_d['U_ID']
        new_password = body_d['new_password']
        otp_code = body_d['otp_code']
        user = User.objects.get(id=U_ID)
        if user.otp_code != otp_code:  
            return JsonResponse({"result": "invalid otp"})
        user.set_password(new_password)  
        user.otp_code = None 
        user.save()
        return JsonResponse({"result": "ok"})
    except Exception as e:
        print(e)
        return JsonResponse({"result": "error "})

@csrf_exempt
def doLogout(request):
    request.session.flush() 
    return JsonResponse({"result": "تم تسجيل الخروج بنجاح"})
@csrf_exempt
def get_wallet_balance(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)
        u_id = body_d["u_id"]
        if not u_id:
            return JsonResponse({"result": "error", "message": "u_id is required"})
        try:
            user = User.objects.get(uuid=u_id)  
        except User.DoesNotExist:
            return JsonResponse({"result": "error", "message": "User does not exist"})
        wallets = Wallet.objects.filter(user=user)
        data = []
        for wallet in wallets:
            wallet_data = {
                "id": wallet.id,
                "balance": wallet.balance,
                "currency":{
                    "code": wallet.currency.code,
                    "name": wallet.currency.name,
                    "exchange_rate": float(wallet.currency.exchange_rate)},
              "wallet_type":{
                    "name": e.wallet_type.name,
                    "label": e.wallet_type.label}}
            data.append(wallet_data)
        return JsonResponse({"result": 'ok', "data": data})
    except Exception as e:
        print(e)
        return JsonResponse({"result": "error"})

@csrf_exempt
def get_latest_transactions(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)

        u_id = body_d["u_id"]
        tx_type = body_d.get("transaction_type") 
        if not u_id:
            return JsonResponse({"result": "error", "message": "User ID (u_id) is required."})

        try:
            user = User.objects.get(uuid=u_id)
        except ObjectDoesNotExist:
            return JsonResponse({"result": "error", "message": "User not found."})

        wallets = Wallet.objects.filter(user=user)
        if not wallets.exists():
            return JsonResponse({"result": "error", "message": "No wallets found for this user."})

        transactions = Transaction.objects.filter(wallet__in=wallets).order_by("-transaction_date", "-transaction_time")

        if tx_type:
            transactions = transactions.filter(transaction_type=tx_type)

        if not transactions.exists():
            return JsonResponse({"result": "ok", "message": "No transactions found."})

        data = []
        for tx in transactions[:10]:
            d = {
                "id": tx.id,
                "type": tx.transaction_type,
                "amount": float(tx.transfer_amount),
                "fee": float(tx.fee),
                "total_amount": float(tx.total_amount),
                "status": tx.status,
                "reference_number": tx.reference_number,
                "recipient_name": tx.recipient.user_name if tx.recipient else (tx.recipient_name or "N/A"),
                "date": tx.transaction_date.strftime("%Y-%m-%d"),  
                "time": tx.transaction_time.strftime("%H:%M:%S"),  
                "wallet_type": tx.wallet.wallet_type.label if tx.wallet else "N/A"
            }
            data.append(d)

        return JsonResponse({"result": "ok", "data": data})

    except json.JSONDecodeError:
        return JsonResponse({"result": "error", "message": "Invalid JSON format."})
    except Exception as e:
        print(f"Error in get_latest_transactions: {str(e)}")
        return JsonResponse({"result": "error", "message": "Server error occurred."})

@csrf_exempt
def get_frequent_recipients(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)
        u_id = body_d["u_id"]

        if not u_id: 
            return JsonResponse({"result": "error", "message": "Missing user ID"})

        try:
            user = User.objects.get(uuid=u_id)
        except User.DoesNotExist:
            return JsonResponse({"result": "error", "message": "User not found"})

        wallets = Wallet.objects.filter(user=user)

        recipients = (
        Transaction.objects.filter(wallet__in=wallets, recipient_name__isnull=False).values("recipient_name").annotate(
            count=Count("recipient_name")).order_by("-count")[:5])
        data = []
        for r in recipients:
            d = {"name": r["recipient_name"], "count": r["count"]}
            data.append(d)
        return JsonResponse({"result": "ok", "data": data})
    except Exception as e:
        print(e)
        return JsonResponse({"result": "error"})

@csrf_exempt
def get_transaction_history(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)
        u_id = body_d["u_id"]

        if not u_id:
            return JsonResponse({"result": "error", "message": "User ID is required"})

        try:
            user = User.objects.get(id=u_id)
            wallets = Wallet.objects.filter(user=user)
            
            transactions = Transaction.objects.filter(wallet__in=wallets).order_by("-transaction_date", "-transaction_time")

            data = []
            for tx in transactions:
                transaction_data = {
                    "id": tx.id,
                    "type": tx.transaction_type,
                    "amount": float(tx.transfer_amount), 
                    "fee": float(tx.fee),
                    "total_amount": float(tx.total_amount),
                    "status": tx.status,
                    "reference_number": tx.reference_number,
                    "recipient_name": tx.recipient.user_name if tx.recipient else "N/A",
                    "date": tx.transaction_date.strftime("%Y-%m-%d"),
                    "time": tx.transaction_time.strftime("%H:%M:%S")
                }
                data.append(transaction_data)

            return JsonResponse({"result": "ok", "data": data})

        except User.DoesNotExist:
            return JsonResponse({"result": "error", "message": "User not found"})
    except Exception as e:
        print(f"Error in get_transaction_history: {str(e)}")
        return JsonResponse({"result": "error", "message": "Server error"})        
@csrf_exempt
def send_transfer(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)

        u_id = body_d["u_id"]
        recipient_phone = body_d["phone"]
        amount = Decimal(str(body_d["amount"]))
        user_name = body_d["name"]
        fee = Decimal(str(body_d["fee"]))

        if amount <= 0 or fee < 0:
            return JsonResponse({"result": "error", "message": "Invalid amount or fee."})

        total_amount = amount + fee

        sender = User.objects.get(id=u_id)
        wallet_type = WalletType.objects.get(name='sender')  
        
        try:
            recipient = User.objects.get(Phone_NO=recipient_phone, user_name=user_name)
            recipient_wallet_type = WalletType.objects.get(name='receiver')
            recipient_wallet = Wallet.objects.get(user=recipient, wallet_type=recipient_wallet_type)
        except User.DoesNotExist:
            return JsonResponse({"result": "error", "message": "Recipient not found."})
        except Wallet.DoesNotExist:
            return JsonResponse({"result": "error", "message": "Recipient wallet not found."})

        wallet_balance_dec = Decimal(str(wallet.balance))
        if wallet_balance_dec < total_amount:
            return JsonResponse({"result": "error", "message": "Insufficient balance."})

        wallet.balance = float(wallet_balance_dec - total_amount)
        recipient_wallet.balance = float(Decimal(str(recipient_wallet.balance)) + amount)
        
        wallet.save()
        recipient_wallet.save()

        tx = Transaction.objects.create(
            transaction_type="send",
            wallet=wallet,
            transfer_amount=float(amount),
            payment_amount=float(total_amount),
            fee=float(fee),
            total_amount=float(total_amount),
            status="completed",
            reference_number=f"SEND-{uuid.uuid4().hex[:12]}",
            sender=sender,
            recipient=recipient,
            transaction_date=timezone.now().date(),
            transaction_time=timezone.now().time()
        )
        
        Notification_Transactions.objects.create(
            transaction=tx,
            message=f"You sent {float(amount)} to {recipient.user_name}"
        )
        return JsonResponse({"result": "ok", "transaction_id": tx.id})

    except User.DoesNotExist:
        return JsonResponse({"result": "error", "message": "Sender not found."})
    except Wallet.DoesNotExist:
        return JsonResponse({"result": "error", "message": "Wallet not found."})
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({"result": "error", "message": str(e)})    
@csrf_exempt
def wallet_topup(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)
        
        user_id = body_d['user_id']
        amount = body_d['amount']
        currency_code = body_d['currency'] 

        if not user_id or amount <= 0 or not currency_code:
            return JsonResponse({'error': 'Incomplete or invalid data'}, status=400)

        try:
            user = User.objects.get(id=user_id)
            currency = Currency.objects.get(code=currency_code)
            
            wallet = Wallet.objects.filter(user=user,currency=currency).first()
            
            if not wallet:
                wallet = Wallet.objects.create(
                    user=user,
                    balance=0.0,
                    currency=currency,
                    wallet_type=WalletType.objects.get_or_create(
                        name='default', 
                        defaults={'label': 'Default Wallet'}
                    )[0]
                )
                return JsonResponse({
                    'message': 'New wallet created and topped up successfully',
                    'balance': wallet.balance,
                    'new_wallet_created': True
                }, status=201)
            wallet.balance += float(amount)
            wallet.save()

            now = timezone.now()
            transaction = Transaction.objects.create(
                reference_number=str(uuid.uuid4()),
                transaction_type='topup',
                sender=user,
                recipient=user,
                wallet=wallet,
                transfer_amount=amount,
                payment_amount=amount,
                fee=0.0,
                total_amount=amount,
                transaction_date=now.date(),
                transaction_time=now.time(),
                status='completed',
            )

            Payment.objects.create(
                transaction=transaction,
                payment_type='WALLET',
                currency=currency,
                amount=amount,
                payment_date=now.date(),
                payment_time=now.time()
            )

            return JsonResponse({
                'message': 'Wallet topped up successfully',
                'balance': wallet.balance,
                'new_wallet_created': False
            }, status=200)

        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Currency.DoesNotExist:
            return JsonResponse({'error': 'Currency not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except KeyError as e:
        return JsonResponse({'error': f'Missing required field: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
@csrf_exempt
def get_incoming_transfer(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)

        u_id = body_d.get("u_id")
        amount_str = body_d.get("amount")
        sender_name = body_d.get("sender_name", "Unknown Sender")

        if u_id is None or amount_str is None:
            return JsonResponse({"result": "error", "message": "u_id and amount are required"})

        try:
            amount = Decimal(str(amount_str))
            if amount <= 0:
                return JsonResponse({"result": "error", "message": "Amount must be positive"})
        except:
            return JsonResponse({"result": "error", "message": "Invalid amount format"})

        try:
            user = User.objects.get(id=u_id)
            wallet_type = WalletType.objects.get(name='receiver')  
            wallet = Wallet.objects.get(user=user, wallet_type=wallet_type)
            service_type = ServiceType.objects.get(name='Transfer Reception')
        except User.DoesNotExist:
            return JsonResponse({"result": "error", "message": "User not found"})
        except Wallet.DoesNotExist:
            return JsonResponse({"result": "error", "message": "Wallet not found"})

        current_balance = Decimal(str(wallet.balance))
        wallet.balance = current_balance + amount
        wallet.save()

        fee = Decimal("0.0")
        total_amount = amount + fee

        tx = Transaction.objects.create(
            service_type=service_type,        
            transaction_type="receive",
            wallet=wallet,
            transfer_amount=amount,
            payment_amount=amount,
            fee=fee,
            total_amount=total_amount,
            status="completed",
            reference_number=f"RECV-{uuid.uuid4().hex[:12]}",
            sender=user,
            recipient=user,
            recipient_name=user.user_name,
            transaction_date=timezone.now().date(),
            transaction_time=timezone.now().time()
        )

        Notification_Transactions.objects.create(
            transaction=tx,
            message=f"You have received {amount} from {sender_name}"
        )

        return JsonResponse({"result": "ok", "transaction_id": tx.id})

    except Exception as e:
        return JsonResponse({"result": "error", "message": f"Failed to receive transfer: {str(e)}"})
@csrf_exempt
def PayBill(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)

        u_id = body_d.get("u_id")
        amount = body_d.get('amount')
        service_name = body_d.get('service_type')  # اسم الخدمة
        code = body_d.get('currency_code', 'USD') 

        if not all([u_id, amount, service_name]):
            return JsonResponse({
                "status": "error", 
                "message": "u_id و amount و service_type حقول مطلوبة"
            })

        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                return JsonResponse({
                    "status": "error", 
                    "message": "المبلغ يجب أن يكون رقمًا موجبًا"
                })
        except:
            return JsonResponse({
                "status": "error", 
                "message": "تنسيق المبلغ غير صحيح"
            })

        
        try:
            user = User.objects.get(id=u_id)
            wallet = Wallet.objects.get(user=user, currency__code=code)
        except User.DoesNotExist:
            return JsonResponse({
                "status": "error", 
                "message": "المستخدم غير موجود"
            })
        except Wallet.DoesNotExist:
            return JsonResponse({
                "status": "error", 
                "message": "المحفظة غير موجودة أو العملة غير مدعومة"
            })

        
        if wallet.balance < float(amount):
            return JsonResponse({
                "status": "error", 
                "message": "الرصيد غير كافي"
            })

      
        try:
            service_type = ServiceType.objects.get(name=service_name)
        except ServiceType.DoesNotExist:
            return JsonResponse({
                "status": "error", 
                "message": f"الخدمة غير موجودة: {service_name}"
            })

        
        wallet.balance -= float(amount)
        wallet.save()

        transaction = Transaction.objects.create(
            transaction_type='bill',
            service_type=service_type,
            wallet=wallet,
            transfer_amount=float(amount),
            payment_amount=float(amount),
            fee=0.0,
            total_amount=float(amount),
            status='completed',
            reference_number=f"BILL-{uuid.uuid4().hex[:8]}",
            sender=user,
            recipient=user,
            transaction_date=timezone.now().date(),
            transaction_time=timezone.now().time(),
        )

        Notification_Transactions.objects.create(
            transaction=transaction,
            message=f"تم دفع {amount} {code} لفواتير {service_type.name}"
        )

        return JsonResponse({
            "status": "success",
            "message": "تم دفع الفاتورة بنجاح",
            "transaction_id": transaction.id,
            "reference_number": transaction.reference_number,
            "remaining_balance": wallet.balance,
            "currency": code,
        })

    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error", 
            "message": "تنسيق JSON غير صحيح"
        })
    except Exception as e:
        print(e)
        return JsonResponse({
            "status": "error", 
            "message": f"خطأ غير متوقع: {str(e)}"
        })
@csrf_exempt
def get_receipts(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)

        u_id = body_d["u_id"]
        if not u_id:
            return JsonResponse({"result": "error", "message": "User ID is required"})

        try:
            user = User.objects.get(id=u_id)
        except User.DoesNotExist:
            return JsonResponse({"result": "error", "message": "User not found"})

        wallets = Wallet.objects.filter(user=user)
        transactions = Transaction.objects.filter(wallet__in=wallets)
        receipts = Receipt.objects.filter(transaction__in=transactions)

        if not receipts:
            return JsonResponse({"result": "error", "message": "No receipts found"})

        data = []
        for r in receipts:
            pdf_url = r.pdf_file.url if hasattr(r.pdf_file, 'url') else None
            d = {
                "transaction_id": r.transaction.id,
                "pdf_url": pdf_url,
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            data.append(d)
        return JsonResponse({"result": "ok", "data": data})
    except Exception as e:
        print(e)
        return JsonResponse({"result": "error", "message": "Failed to fetch receipts"})
@csrf_exempt
def get_notifications(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)
        u_id = body_d.get("u_id")

        if not u_id:
            return JsonResponse({"result": "error", "message": "u_id is required"})

        user = User.objects.get(id=u_id)
        notifications = Notification.objects.filter(user=user).order_by("-created_at")

        is_read = body_d.get("is_read")
        if is_read is not None:
            notifications = notifications.filter(is_read=is_read)

        data = []
        for n in notifications:
            d = {
                "id": n.id,
                "title": n.title,
                "image_url": n.image.url if n.image else None,
                "created_at": n.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "is_read": n.is_read
            }
            data.append(d)
        return JsonResponse({"result": "ok", "data": data})
    except Exception as e:
        print(e)
        return JsonResponse({"result": "error", "message": "Failed to load notifications"})
@csrf_exempt
def mark_notification_as_read(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)
        notification_id = body_d["notification_id"]
        mark_as_read = body_d.get("mark_as_read", True) 

        if not notification_id:
            return JsonResponse({"result": "error", "message": "Notification ID is required"})

        try:
            notification = Notification.objects.get(id=notification_id)
        except Notification.DoesNotExist:
            return JsonResponse({"result": "error", "message": "Notification not found"})

        notification.is_read = mark_as_read
        notification.save()

        return JsonResponse({
            "result": "ok",
            "message": f"Notification marked as {'read' if mark_as_read else 'unread'}"
        })

    except Exception as e:
        print(e)
        return JsonResponse({"result": "error", "message": "Failed to update notification status"})
@csrf_exempt
def login_with_email(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)
        email = body_d.get("email")
        password = body_d.get("password")
        if not email or not password:
            return JsonResponse({'status': 'error', 'message': 'Email and password are required'})

        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            return JsonResponse({
                'status': 'success',
                'message': 'Login successful',
                'user_id': user.id,
                'username': user.user_name,
                'email': user.email,
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid email or password'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Login failed: {str(e)}'})
@csrf_exempt
def get_paid_bills(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)
        u_id = body_d["u_id"]
        service_name = body_d['service_type']
        date_from = body_d.get("date_from") 
        date_to = body_d.get("date_to")
        if not u_id:
            return JsonResponse({'result': 'error', 'message': 'User ID is required'})
        try:
            user = User.objects.get(id=u_id)
        except User.DoesNotExist:
            return JsonResponse({'result': 'error', 'message': 'User not found'})

        wallets = Wallet.objects.filter(user=user)
        transactions = Transaction.objects.filter(wallet__in=wallets,transaction_type="bill")

        if service_type:
            service_type = ServiceType.objects.get(name=service_name)
            transactions = transactions.filter(service_type=service_type)
        if date_from:
            transactions = transactions.filter(transaction_date__gte=parse_date(date_from))
        if date_to:
            transactions = transactions.filter(transaction_date__lte=parse_date(date_to))

        
        data = []
        for tx in transactions.order_by("-transaction_date", "-transaction_time"):
                receipt = Receipt.objects.filter(transaction=tx).first()
                notification = Notification_Transactions.objects.filter(transaction=tx).first()

                data.append({
                    "transaction_id": tx.id,
                    "amount": float(tx.transfer_amount),
                    "service_type": tx.service_type,
                    "date": tx.transaction_date.strftime("%Y-%m-%d"),
                    "time": tx.transaction_time.strftime("%H:%M:%S"),
                    "status": tx.status,
                    "receipt_url": receipt.pdf_file.url if receipt else None,
                    "notification_message": notification.message if notification else None,
                })
        return JsonResponse({"result": "ok", "data": data})

    except Exception as e:
        print("Error in get_paid_bills:", e)
        return JsonResponse({"result": "error", "message": "Failed to retrieve invoices"})
@csrf_exempt
def get_transaction_details(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)
        transaction_id = body_d["transaction_id"]
        u_id = body_d["u_id"]

        try:
            user = User.objects.get(id=u_id)
            transaction = Transaction.objects.get(id=transaction_id)
        except User.DoesNotExist:
            return JsonResponse({"result": "error", "message": "User not found"})
        except Transaction.DoesNotExist:
            return JsonResponse({"result": "error", "message": "Transaction not found"})

        is_allowed = (
            transaction.sender == user or 
            transaction.recipient == user or 
            (transaction.wallet and transaction.wallet.user == user)
        )
        
        if not is_allowed:
            return JsonResponse({"result": "error", "message": "Unauthorized access"})

        data = {
            "id": transaction.id,
            "reference_number": transaction.reference_number,
            "transaction_type": transaction.transaction_type,
            "status": transaction.status,
            "transfer_amount": float(transaction.transfer_amount),
            "payment_amount": float(transaction.payment_amount),
            "fee": float(transaction.fee),
            "total_amount": float(transaction.total_amount),
            "transaction_date": transaction.transaction_date.strftime("%Y-%m-%d"),
            "transaction_time": transaction.transaction_time.strftime("%H:%M:%S"),
            "service_type": {
                       "id": transaction.service_type.id,
                       "name": transaction.service_type.name
                      } if transaction.service_type else None,
            "sender": {
                "id": transaction.sender.id,
                "name": transaction.sender.name 
            } if transaction.sender else None,
            "recipient": {
                "id": transaction.recipient.id,
                "name": transaction.recipient.name
            } if transaction.recipient else None,
            "wallet": {
                "id": transaction.wallet.id,
                "balance": transaction.wallet.balance
            } if transaction.wallet else None,
        }

        return JsonResponse({"result": "ok", "data": data})

    except json.JSONDecodeError:
        return JsonResponse({"result": "error", "message": "Invalid JSON format"})
    except KeyError as e:
        return JsonResponse({"result": "error", "message": f"Missing field: {str(e)}"})
    except Exception as e:
        print(f"Error in get_transaction_details: {str(e)}")
        return JsonResponse({"result": "error", "message": "Internal server error"})
@csrf_exempt
def get_transactions_paginated(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)
        u_id = body_d["u_id"]
        page_number = int(body_d.get("page", 1))
        page_size = int(body_d.get("page_size", 2))
        transaction_type = body_d.get("transaction_type")  

        user = User.objects.get(id=u_id)
        wallets = Wallet.objects.filter(user=user)
        transactions = Transaction.objects.filter(wallet__in=wallets)
        
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
            
        transactions = transactions.order_by('-transaction_date', '-transaction_time')

        paginator = Paginator(transactions, page_size)
        page = paginator.get_page(page_number)

        data = []
        for tx in page.object_list:
            transaction_data = {
                "id": tx.id,
                "amount": float(tx.transfer_amount),  
                "type": tx.transaction_type,
                "status": tx.status,
                "date": tx.transaction_date.strftime("%Y-%m-%d"),  
                "time": tx.transaction_time.strftime("%H:%M:%S"),  
                "recipient": {
                    "id": tx.recipient.id if tx.recipient else None,
                    "name": tx.recipient.name if tx.recipient else tx.recipient_name
                } if tx.recipient or hasattr(tx, 'recipient_name') else None,
                "reference_number": tx.reference_number
            }
            data.append(transaction_data)

        return JsonResponse({
            "result": "ok",
            "transactions": data,
            "total_pages": paginator.num_pages,
            "current_page": int(page_number),
            "page_size": int(page_size),
            "total_transactions": paginator.count
        })

    except User.DoesNotExist:
        return JsonResponse({"result": "error", "message": "User not found"})
    except Exception as e:
        print(f"Error in get_transactions_paginated: {str(e)}")
        return JsonResponse({"result": "error", "message": "Failed to retrieve operations"})

@csrf_exempt
def get_user_transfers(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)
        
        u_id = body_d["u_id"]
        page_number = int(body_d.get("page", 1))
        page_size = int(body_d.get("page_size", 10))

        if not u_id:
            return JsonResponse({'status': 'error', 'message': 'User ID is required'})

        try:
            user = User.objects.get(id=u_id)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'})

        wallets = Wallet.objects.filter(user=user)

        transfers = Transaction.objects.filter(
            wallet__in=wallets,
            transaction_type='send'  
        ).order_by('-transaction_date', '-transaction_time')  

        paginator = Paginator(transfers, page_size)
        page = paginator.get_page(page_number)

        data = []
        for tx in page.object_list:
            data.append({
                "id": tx.id,
                "amount": float(tx.transfer_amount),  
                "to_user": tx.recipient.user_name if tx.recipient else "N/A", 
                "status": tx.status,
                "transaction_date": tx.transaction_date.strftime("%Y-%m-%d"),  
                "transaction_time": tx.transaction_time.strftime("%H:%M:%S"),  
                "reference_number": tx.reference_number,
            })

        return JsonResponse({
            "status": "success",
            "transfers": data,
            "total_pages": paginator.num_pages,
            "current_page": int(page_number),
            "page_size": int(page_size)
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
@csrf_exempt
def update_recipient(request):
    try:
        body = request.body.decode('utf-8')
        body_d = json.loads(body)

        contact_id = body_d.get('contact_id')
        new_name = body_d.get('new_name')
        new_phone = body_d.get('new_phone')

        if not contact_id:
            return JsonResponse({'status': 'error', 'message': 'contact_id is required'})

        contact = FrequentContact.objects.get(id=contact_id)

        if new_name:
            contact.name = new_name
        if new_phone:
            contact.phone_number = new_phone
        contact.save()

        return JsonResponse({'status': 'success', 'contact_id': contact.id})
    except FrequentContact.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'جهة الاتصال غير موجودة'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
def delete_frequent_contact(request):
    try:
        body=request.body.decode('utf-8')
        body_d=json.loads(body)

        ccontact_id =body_d['contact_id']
        if not ccontact_id:
            return JsonResponse({'status': 'error', 'message': 'ccontact_id is required'})
        contact = FrequentContact.objects.get(id=ccontact_id)
        contact.delete()
        return JsonResponse({'status': 'success', 'message': 'Contact deleted successfully'})
    except FrequentContact.DoesNotExist:
        return JsonResponse({'status': 'reeoe', 'message': 'Contact not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
@csrf_exempt
def get_frequent_contacts(request):
    try:
        body=request.body.decode('utf-8')
        body_d=json.loads(body)
        user_id = body_d['user_id']
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'user_id is required'},)

        contacts = FrequentContact.objects.filter(user_id=user_id).order_by('-last_used')[:10]

        contacts_data = [{
            'id': c.id,
            'name': c.name,
            'phone': c.phone_number,
            'last_used': c.last_used.strftime('%Y-%m-%d %H:%M')
        } for c in contacts]

        return JsonResponse({'status': 'success','count': len(contacts_data),'contacts': contacts_data})


    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error', 'message': str(e)})
@csrf_exempt
def GetBalanceHistory(request):
    try:
        body=request.body.decode('utf-8')
        body_d=json.loads(body)
        u_id = body_d['u_id']
        time_range = body_d.get('range', 'week')  

        if not u_id:
            return JsonResponse({'status': 'error', 'message': 'u_id is required'})

        end_date = timezone.now()
        if time_range == 'week':
            start_date = end_date - timedelta(days=7)
        elif time_range == 'month':
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=365)

        transactions = Transaction.objects.filter(Q(sender_id=u_id) | Q(recipient_id=u_id),
            transaction_date__range=[start_date, end_date],status='completed').order_by('transaction_date')

        daily_balances = {}
        balance = 0.0

        for txn in transactions:
            date_str = txn.transaction_date.strftime('%Y-%m-%d')
            if date_str not in daily_balances:
                daily_balances[date_str] = balance

            if txn.transaction_type == 'receive':
                balance += float(txn.transfer_amount)
            elif txn.transaction_type == 'send':
                balance -= float(txn.transfer_amount)

            daily_balances[date_str] = balance

        labels = list(daily_balances.keys())
        values = list(daily_balances.values())

        return JsonResponse({
            'status': 'success',
            'data': {
                'labels': labels,
                'values': values,
                'currency': 'SYP'
            }})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
@csrf_exempt
def GetSpendingAnalysis(request):
    try:
        body=request.body.decode('utf-8')
        body_d=json.loads(body)
        user_id =body_d['user_id']
        
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'user_id is required'})

        categories = Transaction.objects.filter(
            sender_id=user_id,
            transaction_type='send',
            status='completed'
        ).values('transaction_type').annotate(
            total=Sum('transfer_amount'),
            count=Count('id')
        ).order_by('-total')

        monthly_spending = Transaction.objects.filter(
            sender_id=user_id,
            transaction_type='send',
            status='completed'
        ).annotate(
            month=TruncMonth('transaction_date')
        ).values('month').annotate(
            total=Sum('transfer_amount')
        ).order_by('month')

        return JsonResponse({
            'status': 'success',
            'by_category': list(categories),
            'monthly': list(monthly_spending)
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
@csrf_exempt
def GetUserPreferences(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'status':'error','message':'user_id is required'})
    try:
        pref = UserPreference.objects.get(user__id=user_id)
        data = {
            'default_currency': pref.default_currency.code if pref.default_currency else None,
            'language': pref.language,
            'theme': pref.theme,
        }
        return JsonResponse({'status':'success','preferences':data})
    except UserPreference.DoesNotExist:
        return JsonResponse({'status':'error','message':'Preferences not found'})
        
@csrf_exempt
def update_user_preferences(request):
    try:
        body = json.loads(request.body)
        user_id = body.get('user_id')
        if not user_id:
            return JsonResponse({'status':'error','message':'user_id is required'})
        pref, created = UserPreference.objects.get_or_create(user_id=user_id)
        if 'default_currency' in body:
            pref.default_currency = Currency.objects.get(code=body['default_currency'])
        if 'language' in body:
            pref.language = body['language']
        if 'theme' in body:
            pref.theme = body['theme']
        pref.save()
        return JsonResponse({'status':'success','created':created})
    except Currency.DoesNotExist:
        return JsonResponse({'status':'error','message':'Invalid currency code'})
    except Exception as e:
        return JsonResponse({'status':'error','message':str(e)})

def home_page(request):
    """الصفحة الرئيسية للتطبيق"""
    html_content = """
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>نظام الدفع الإلكتروني</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin: 50px; }
            h1 { color: #2c3e50; }
            .button { 
                display: inline-block; 
                padding: 12px 24px; 
                margin: 10px; 
                background: #3498db; 
                color: white; 
                text-decoration: none; 
                border-radius: 5px; 
                font-weight: bold; 
            }
            .button:hover { background: #2980b9; }
        </style>
    </head>
    <body>
        <h1>مرحباً بك في نظام الدفع الإلكتروني</h1>
        <p>اختر الواجهة التي تريد الوصول إليها:</p>
        
        <div>
            <a href="/admin/" class="button">لوحة الإدارة (Django Admin)</a>
            <a href="/app/" class="button">التطبيق الرئيسي</a>
            <a href="/swagger/" class="button">Swagger API Documentation</a>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)