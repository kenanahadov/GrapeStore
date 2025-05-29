from django.contrib import admin
from .models import *
class ImgInline(admin.TabularInline):
    model=ProductImage
    extra=1
class ProductAdmin(admin.ModelAdmin):
    inlines=[ImgInline]
admin.site.register(Product,ProductAdmin)
admin.site.register(Address)
admin.site.register(PaymentMethod)
admin.site.register(Order)
admin.site.register(OrderItem)



# ---------------------------------------------------------------------------
# 🚀  Analytics tab – proper monkey‑patch
# ---------------------------------------------------------------------------
from django.urls import path
from django.db.models import Sum
from django.template.response import TemplateResponse
from django.utils import timezone
from datetime import timedelta

def _analytics_view(request):
    from .models import OrderItem
    now = timezone.now()
    last_90 = now - timedelta(days=90)
    qs = (OrderItem.objects
          .filter(order__created__gte=last_90)
          .values('product__name')
          .annotate(units=Sum('qty'), revenue=Sum('price'))
          .order_by('-units')[:20])

    return TemplateResponse(request,
        'admin/analytics.html',
        {'top_products': qs, 'since': last_90.date(), 'today': now.date()}
    )

# Cache original method once, then extend
_original_get_urls = admin.AdminSite.get_urls
def _patched_get_urls(self):
    urls = _original_get_urls(self)
    extra = [path('analytics/', self.admin_view(_analytics_view), name='analytics')]
    return extra + urls
admin.AdminSite.get_urls = _patched_get_urls
