from django.contrib import admin
from .models import *
@admin.register(Customer_user)
class CustomerUserAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:  # إذا كان هذا هو إنشاء مستخدم جديد
            obj.set_password(form.cleaned_data['password'])  # تأكد من تشفير كلمة المرور
        super().save_model(request, obj, form, change)
admin.site.register(Message)

admin.site.register(Notfications)