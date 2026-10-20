from django import forms
from django.contrib import admin
from .models import AccessCode, CodeRedemption, Payment, PremiumAccess, PremiumPlan

admin.site.register(PremiumPlan)
admin.site.register(PremiumAccess)
admin.site.register(CodeRedemption)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order_id", "user", "provider", "amount_usd", "status", "paid_at")
    list_filter = ("status", "provider")
    readonly_fields = [f.name for f in Payment._meta.fields]
    def has_add_permission(self, request): return False


class AccessCodeForm(forms.ModelForm):
    plain_code = forms.CharField(required=False, min_length=6, max_length=64,
                                 help_text="Set only when creating. Stored as a hash; cannot be viewed later.")
    class Meta:
        model = AccessCode
        fields = ["kind", "label", "is_active", "max_uses", "expires_at", "grant_days"]


@admin.register(AccessCode)
class AccessCodeAdmin(admin.ModelAdmin):
    form = AccessCodeForm
    list_display = ("label", "kind", "hint", "is_active", "used_count", "max_uses", "expires_at")
    fields = ("plain_code", "kind", "label", "is_active", "max_uses", "expires_at", "grant_days")

    def save_model(self, request, obj, form, change):
        plain = form.cleaned_data.get("plain_code")
        if not change:
            if not plain:
                raise forms.ValidationError("Enter the code for a new entry.")
            from .codes import hash_code, normalize_code
            obj.code_hash, obj.hint = hash_code(plain), normalize_code(plain)[-2:]
        super().save_model(request, obj, form, change)
