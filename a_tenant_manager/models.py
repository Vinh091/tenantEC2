from django.db import models
from django.contrib.auth.models import User
from django_tenants.models import TenantMixin, DomainMixin

class Tenant(TenantMixin):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    
    auto_create_schema = True
    auto_drop_schema = True
    
class Domain(DomainMixin):
    pass
class TenantMember(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default= False )
    
    class Meta: 
        unique_together = ('user', 'tenant')
    def __str__(self):
        return f"{self.tenant.name} - {self.user}{' (Admin)' if self.is_admin else ''}"
