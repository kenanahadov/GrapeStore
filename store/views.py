from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q,Sum
from decimal import Decimal
from .models import *
from .forms import RegisterForm,AddressForm,PaymentForm

def home(request):
    q=request.GET.get('q','')
    products=Product.objects.filter(Q(name__icontains=q)|Q(description__icontains=q)) if q else Product.objects.all()
    return render(request,'store/home.html',{'products':products,'query':q})

def product_detail(request,pk):
    product=get_object_or_404(Product,pk=pk)
    in_wishlist=False
    if request.user.is_authenticated:
        in_wishlist=Wishlist.objects.filter(user=request.user,products=product).exists()
    return render(request,'store/product_detail.html',{'product':product,'in_wishlist':in_wishlist})

def _cart(request):
    cart=request.session.get('cart',{})
    items=[]
    total=Decimal('0')
    for pid,qty in cart.items():
        p=Product.objects.get(pk=int(pid))
        subtotal=p.price*qty
        total+=subtotal
        items.append({'product':p,'qty':qty,'subtotal':subtotal})
    return items,total

@user_passes_test(lambda u:u.is_staff)
def dashboard(request):
    stats={'users':User.objects.count(),
           'orders':Order.objects.count(),
           'revenue':Order.objects.aggregate(Sum('total'))['total__sum'] or 0}
    return render(request,'store/dashboard.html',stats)

def add_cart(request,pk):
    cart=request.session.get('cart',{})
    cart[str(pk)]=cart.get(str(pk),0)+1
    request.session['cart']=cart
    return redirect('cart')

def remove_cart(request,pk):
    cart=request.session.get('cart',{})
    cart.pop(str(pk),None)
    request.session['cart']=cart
    return redirect('cart')

def cart_view(request):
    items,total=_cart(request)
    return render(request,'store/cart.html',{'items':items,'total':total})

@login_required
def toggle_wishlist(request,pk):
    product=get_object_or_404(Product,pk=pk)
    wl,_=Wishlist.objects.get_or_create(user=request.user)
    if wl.products.filter(pk=pk).exists():
        wl.products.remove(product)
    else:
        wl.products.add(product)
    return redirect(request.META.get('HTTP_REFERER','home'))

@login_required
def wishlist(request):
    wl=Wishlist.objects.filter(user=request.user).first()
    products=wl.products.all() if wl else []
    return render(request,'store/wishlist.html',{'products':products})

@login_required
def checkout(request):
    items,total=_cart(request)
    if not items: return redirect('cart')
    addresses=Address.objects.filter(user=request.user)
    payments=PaymentMethod.objects.filter(user=request.user)
    addr_form=AddressForm(prefix='addr')
    pay_form=PaymentForm(prefix='pay')
    if request.method=='POST':
        addr_sel=request.POST.get('address')
        pay_sel=request.POST.get('payment')
        if addr_sel=='new' or not addresses.exists():
            addr_form=AddressForm(request.POST,prefix='addr')
            if addr_form.is_valid():
                address=addr_form.save(commit=False); address.user=request.user; address.save()
            else: return render(request,'store/checkout.html',locals())
        else:
            address=Address.objects.get(pk=int(addr_sel))
        if pay_sel=='new' or not payments.exists():
            pay_form=PaymentForm(request.POST,prefix='pay')
            if pay_form.is_valid():
                payment=pay_form.save(commit=False); payment.user=request.user; payment.save()
            else: return render(request,'store/checkout.html',locals())
        else:
            payment=PaymentMethod.objects.get(pk=int(pay_sel))
        order=Order.objects.create(user=request.user,address=address,payment=payment,total=total)
        for it in items:
            OrderItem.objects.create(order=order,product=it['product'],qty=it['qty'],price=it['product'].price)
        request.session['cart']={}
        return redirect('account')
    est='June 1'
    return render(request,'store/checkout.html',locals())

@login_required
def account(request):
    orders=Order.objects.filter(user=request.user).order_by('-created')
    return render(request,'store/account.html',{'orders':orders})

@login_required
def settings_view(request):
    addresses=Address.objects.filter(user=request.user)
    payments=PaymentMethod.objects.filter(user=request.user)
    addr_form=AddressForm(prefix='addr')
    pay_form=PaymentForm(prefix='pay')
    if request.method=='POST':
        if 'add_addr' in request.POST:
            addr_form=AddressForm(request.POST,prefix='addr')
            if addr_form.is_valid():
                a=addr_form.save(commit=False); a.user=request.user; a.save(); return redirect('settings')
        elif 'add_pay' in request.POST:
            pay_form=PaymentForm(request.POST,prefix='pay')
            if pay_form.is_valid():
                p=pay_form.save(commit=False); p.user=request.user; p.save(); return redirect('settings')
    return render(request,'store/settings.html',locals())

def register(request):
    if request.method=='POST':
        form=RegisterForm(request.POST)
        if form.is_valid():
            user=form.save()
            Wishlist.objects.create(user=user)
            login(request,user)
            return redirect('home')
    else:
        form=RegisterForm()
    return render(request,'store/register.html',{'form':form})
