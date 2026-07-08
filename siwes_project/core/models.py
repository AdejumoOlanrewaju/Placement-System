from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

# ─────────────────────────────────────────
# CUSTOM USER (base for all user types)
# ─────────────────────────────────────────

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('company', 'Company'),
        ('admin', 'Admin')
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='core_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='core_user_permissions_set',
        blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
    
# ─────────────────────────────────────────
# NIGERIA LOCATION
# ─────────────────────────────────────────

class State(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class LGA(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='lgas') 
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"
    
# ─────────────────────────────────────────
# STUDENT PROFILE
# ─────────────────────────────────────────
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    matric_number = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    institution = models.CharField(max_length=150)
    skills = models.TextField(blank=True, help_text="Comma-separated skills e.g. Python, Django, SQL")
    preferred_state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    preferred_lga = models.ForeignKey(LGA, on_delete=models.SET_NULL, null=True, blank=True)
    profile_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department}"


# ─────────────────────────────────────────
# COMPANY PROFILE (supports Option 4)
# ─────────────────────────────────────────
class CompanyProfile(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=200)
    industry = models.CharField(max_length=100)
    description = models.TextField()
    address = models.TextField()
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    lga = models.ForeignKey(LGA, on_delete=models.SET_NULL, null=True)
    website = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # Option 4
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name} [{self.status}]"

    @property
    def is_verified(self):
        return self.status == 'verified'


# ─────────────────────────────────────────
# PLACEMENT LISTING
# ─────────────────────────────────────────
class PlacementListing(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    department_required = models.CharField(max_length=100, help_text="e.g. Computer Science, Engineering")
    skills_required = models.TextField(help_text="Comma-separated skills")
    description = models.TextField()
    slots_available = models.PositiveIntegerField(default=1)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    lga = models.ForeignKey(LGA, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} @ {self.company.company_name}"


# ─────────────────────────────────────────
# APPLICATION (supports Option 2 — status tracking)
# ─────────────────────────────────────────
class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('offered',  'Offered'),       
        ('offer_accepted', 'Offer Accepted'),
        ('offer_declined', 'Offer Declined'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    listing = models.ForeignKey(PlacementListing, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    company_note = models.TextField(blank=True, help_text="Feedback from company")

    class Meta:
        unique_together = ('student', 'listing')  # student can't apply twice to same listing

    def __str__(self):
        return f"{self.student} → {self.listing} [{self.status}]"


# ─────────────────────────────────────────
# AI RECOMMENDATION LOG (supports Option 1)
# ─────────────────────────────────────────
class AIRecommendation(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='recommendations')
    listing = models.ForeignKey(PlacementListing, on_delete=models.CASCADE)
    reason = models.TextField()  # AI-generated explanation
    score = models.FloatField(default=0.0)  # ranking score
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score']

    def __str__(self):
        return f"Rec: {self.student} → {self.listing} (score: {self.score})"