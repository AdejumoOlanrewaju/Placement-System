from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import PlacementListing, User, StudentProfile, CompanyProfile, State, LGA, Application


# ─────────────────────────────────────────
# STUDENT REGISTRATION FORM
# ─────────────────────────────────────────
class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name  = forms.CharField(max_length=100)
    email      = forms.EmailField()
    phone      = forms.CharField(max_length=20)

    # StudentProfile fields
    matric_number = forms.CharField(max_length=50)
    department    = forms.CharField(max_length=100)
    institution   = forms.CharField(max_length=150)
    skills        = forms.CharField(
                        widget=forms.Textarea(attrs={'rows': 2}),
                        help_text="e.g. Python, Django, SQL",
                        required=False
                    )
    preferred_state = forms.ModelChoiceField(
                        queryset=State.objects.all(),
                        required=False
                      )
    preferred_lga   = forms.ModelChoiceField(
                        queryset=LGA.objects.none(),  # populated dynamically
                        required=False
                      )

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if a state was submitted, load that state's LGAs for validation
        if 'preferred_state' in self.data:
            try:
                state_id = int(self.data.get('preferred_state'))
                self.fields['preferred_lga'].queryset = LGA.objects.filter(state_id=state_id)
            except (ValueError, TypeError):
                self.fields['preferred_lga'].queryset = LGA.objects.none()
        elif self.instance.pk:
            # editing existing profile — load current LGAs
            self.fields['preferred_lga'].queryset = self.instance.student_profile.preferred_state.lgas.all()


    def save(self, commit=True):
        user           = super().save(commit=False)
        user.role      = 'student'
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        user.email      = self.cleaned_data['email']
        user.phone      = self.cleaned_data['phone']
        if commit:
            user.save()
            StudentProfile.objects.create(
                user            = user,
                matric_number   = self.cleaned_data['matric_number'],
                department      = self.cleaned_data['department'],
                institution     = self.cleaned_data['institution'],
                skills          = self.cleaned_data['skills'],
                preferred_state = self.cleaned_data['preferred_state'],
                preferred_lga   = self.cleaned_data['preferred_lga'],
            )
        return user


# ─────────────────────────────────────────
# COMPANY REGISTRATION FORM
# ─────────────────────────────────────────
class CompanyRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, label="Contact Person First Name")
    last_name  = forms.CharField(max_length=100, label="Contact Person Last Name")
    email      = forms.EmailField()
    phone      = forms.CharField(max_length=20)

    # CompanyProfile fields
    company_name = forms.CharField(max_length=200)
    industry     = forms.CharField(max_length=100)
    description  = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    address      = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    website      = forms.URLField(required=False)
    state        = forms.ModelChoiceField(queryset=State.objects.all())
    lga          = forms.ModelChoiceField(queryset=LGA.objects.none())

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['lga'].queryset = LGA.objects.filter(state_id=state_id)
            except (ValueError, TypeError):
                self.fields['lga'].queryset = LGA.objects.none() 

    def save(self, commit=True):
        user            = super().save(commit=False)
        user.role       = 'company'
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        user.email      = self.cleaned_data['email']
        user.phone      = self.cleaned_data['phone']
        if commit:
            user.save()
            CompanyProfile.objects.create(
                user         = user,
                company_name = self.cleaned_data['company_name'],
                industry     = self.cleaned_data['industry'],
                description  = self.cleaned_data['description'],
                address      = self.cleaned_data['address'],
                website      = self.cleaned_data.get('website', ''),
                state        = self.cleaned_data['state'],
                lga          = self.cleaned_data['lga'],
                status       = 'pending',  # Option 4 — always starts pending
            )
        return user


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter']
        widgets = {
            'cover_letter' : forms.Textarea(attrs= {
                'rows' : 5,
                'placeholder' : 'Briefly explain why you are applying for this placement...'
            })
        }

class PlacementListingForm(forms.ModelForm):
    state = forms.ModelChoiceField(queryset=State.objects.all())
    lga   = forms.ModelChoiceField(queryset=LGA.objects.none())

    class Meta:
        model  = PlacementListing
        fields = [
            'title', 'department_required', 'skills_required',
            'description', 'slots_available', 'deadline', 'state', 'lga'
        ]
        widgets = {
            'description'     : forms.Textarea(attrs={'rows': 3}),
            'skills_required' : forms.Textarea(attrs={'rows': 2}),
            'deadline'        : forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['lga'].queryset = LGA.objects.filter(state_id=state_id)
            except (ValueError, TypeError):
                self.fields['lga'].queryset = LGA.objects.none()
        elif self.instance.pk:
            self.fields['lga'].queryset = LGA.objects.filter(state=self.instance.state)

# ─────────────────────────────────────────
# LOGIN FORM
# ─────────────────────────────────────────
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

# ─────────────────────────────────────────
# Admin Register Company FORM
# ─────────────────────────────────────────
class AdminRegisterCompanyForm(forms.Form):
    # Contact person
    first_name = forms.CharField(max_length=100)
    last_name  = forms.CharField(max_length=100)
    email      = forms.EmailField()
    phone      = forms.CharField(max_length=20)

    # Company details
    company_name = forms.CharField(max_length=200)
    industry     = forms.CharField(max_length=100)
    description  = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    address      = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    website      = forms.URLField(required=False)
    state        = forms.ModelChoiceField(queryset=State.objects.all())
    lga          = forms.ModelChoiceField(queryset=LGA.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['lga'].queryset = LGA.objects.filter(state_id=state_id)
            except (ValueError, TypeError):
                self.fields['lga'].queryset = LGA.objects.none()