from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, CompanyProfile, State, LGA, PlacementListing, Application, AIRecommendation

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff']
    list_filter   = ['role', 'is_staff']
    search_fields = ['username', 'email']
    fieldsets     = UserAdmin.fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone')}),
    )

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'matric_number', 'department', 'institution']
    search_fields = ['matric_number', 'department']

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display  = ['company_name', 'industry', 'status', 'state', 'created_at']
    list_filter   = ['status']
    search_fields = ['company_name']

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(LGA)
class LGAAdmin(admin.ModelAdmin):
    list_display  = ['name', 'state']
    list_filter   = ['state']

@admin.register(PlacementListing)
class PlacementListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'department_required', 'slots_available', 'is_active']
    list_filter  = ['is_active']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['student', 'listing', 'status', 'applied_at']
    list_filter  = ['status']

@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ['student', 'listing', 'score', 'generated_at']