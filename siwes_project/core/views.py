from email.mime import application
from urllib import request
import secrets
import string

from django.utils import timezone

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# from urllib3 import request
from .forms import AdminRegisterCompanyForm, StudentRegistrationForm, CompanyRegistrationForm, LoginForm, ApplicationForm, PlacementListingForm
from .models import LGA, AIRecommendation, StudentProfile, PlacementListing, Application, State, CompanyProfile, User
from django.http import JsonResponse
from .ai import generate_recommendations

from .sms import notify_student_status_change, notify_admin_offer_accepted, notify_company_offer_response
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command



# ─────────────────────────────────────────
# HELPER — generate random password
# ─────────────────────────────────────────
def generate_password(length=10):
    chars    = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def generate_password_name(company_name):
    # takes first word of company name + fixed suffix + 3 digit number
    first_word = company_name.split()[0].lower()
    number     = str(secrets.randbelow(900) + 100)  # 100-999
    return f"{first_word}@{number}"



@csrf_exempt
def setup_view(request):
    from core.models import User, State

    step = request.POST.get('step', '')

    # already fully set up
    if User.objects.filter(role='admin').exists() and step == '':
        return HttpResponse("""
            <!DOCTYPE html><html><body style='font-family:sans-serif;max-width:500px;margin:100px auto;padding:20px;'>
            <h2 style='color:green;'>✅ System Already Set Up</h2>
            <a href='/login/'>Go to Login →</a>
            </body></html>
        """)

    if request.method == 'POST':

        if step == 'migrate':
            call_command('migrate', '--run-syncdb')
            return HttpResponse(page('Step 1 Done — Migrations complete', 'seed_nigeria', 'Seed Nigeria States & LGAs'))

        elif step == 'seed_nigeria':
            call_command('seed_nigeria')
            return HttpResponse(page('Step 2 Done — Nigeria data seeded', 'seed_companies', 'Seed Companies'))

        elif step == 'seed_companies':
            call_command('seed_companies')
            return HttpResponse(page('Step 3 Done — Companies seeded', 'create_admin', 'Create Admin Account'))

        elif step == 'create_admin':
            if not User.objects.filter(role='admin').exists():
                User.objects.create_superuser(
                    username   = 'admin',
                    email      = 'admin@siwes.com',
                    password   = 'admin2024',
                    first_name = 'System',
                    last_name  = 'Admin',
                    role       = 'admin',
                )
            return HttpResponse("""
                <!DOCTYPE html><html><body style='font-family:sans-serif;max-width:500px;margin:100px auto;padding:20px;'>
                <h2 style='color:green;'>✅ Setup Complete!</h2>
                <p><strong>Admin credentials:</strong></p>
                <p>Username: <strong>admin</strong></p>
                <p>Password: <strong>admin2024</strong></p>
                <br>
                <a href='/login/' style='background:#2563eb;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;'>
                    Go to Login →
                </a>
                </body></html>
            """)

    # initial page
    return HttpResponse(page('SIWES System Setup', 'migrate', 'Step 1 — Run Migrations'))


def page(title, next_step, button_text):
    return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SIWES Setup</title>
            <style>
                body {{ font-family: sans-serif; max-width: 500px; margin: 100px auto; padding: 20px; }}
                h2 {{ color: #0f172a; }}
                p {{ color: #64748b; }}
                button {{
                    background: #2563eb; color: #fff; border: none;
                    padding: 12px 28px; border-radius: 8px;
                    font-size: 15px; cursor: pointer; margin-top: 16px;
                }}
                button:hover {{ background: #1d4ed8; }}
                .done {{ color: green; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h2>{title}</h2>
            <form method='POST' action='/setup/'>
                <input type='hidden' name='step' value='{next_step}'>
                <button type='submit'>{button_text}</button>
            </form>
        </body>
        </html>
    """

# ─────────────────────────────────────────
# REGISTER — STUDENT
# ─────────────────────────────────────────
def register_student(request):
    if request.user.is_authenticated:
        return redirect('student_dashboard')

    form = StudentRegistrationForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully. Welcome!")
            return redirect('student_dashboard')
        else:
            messages.error(request, "Please fix the errors below.")

    return render(request, 'auth/register_student.html', {'form': form})


# ─────────────────────────────────────────
# REGISTER — COMPANY
# ─────────────────────────────────────────
def register_company(request):
    if request.user.is_authenticated:
        return redirect('company_dashboard')

    form = CompanyRegistrationForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Company registered. Await admin verification.")
            return redirect('company_dashboard')
        else:
            print("FORM ERRORS: ", form.errors)
            print("NON FIELD ERRORS:", form.non_field_errors())  # ← and this
            messages.error(request, "Please fix the errors below.")

    return render(request, 'auth/register_company.html', {'form': form})


# ─────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'student':
            return redirect('student_dashboard')
        elif request.user.role == 'company':
            return redirect('company_dashboard')
        elif request.user.role == 'admin':
            return redirect('admin_dashboard')

    form = LoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user     = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                # messages.success(request, f"Welcome back, {user.first_name}!")
                if user.role == 'student':
                    messages.success(request, f"Welcome back, {user.first_name}!")
                    return redirect('student_dashboard')
                elif user.role == 'company':
                    messages.success(request, f"Welcome back, {user.company_profile.company_name}!")
                    return redirect('company_dashboard')
                elif user.role == 'admin':
                    name = user.first_name or user.username
                    messages.success(request, f"Welcome back, {name}!")
                    return redirect('admin_dashboard')
            else:
                messages.error(request, "Invalid username or password.")

    return render(request, 'auth/login.html', {'form': form})


# ─────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# ─────────────────────────────────────────
# AJAX — load LGAs when state is selected
# ─────────────────────────────────────────
def load_lgas(request):
    state_id = request.GET.get('state_id')
    lgas     = LGA.objects.filter(state_id=state_id).values('id', 'name')
    return JsonResponse(list(lgas), safe=False)


@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('login')

    profile      = get_object_or_404(StudentProfile, user=request.user)
    applications = Application.objects.filter(student=profile).select_related('listing__company').order_by('-applied_at')
    
    # stats
    total_applied = applications.count()
    pending       = applications.filter(status='pending').count()
    accepted      = applications.filter(status='accepted').count()
    rejected      = applications.filter(status='rejected').count()

    # load saved recommendations
    recommendations = AIRecommendation.objects.filter(
        student=profile,
        listing__is_active=True,   
        listing__company__status='verified'
    ).select_related('listing__company', 'listing__state', 'listing__lga').order_by('-score')[:5]

    applied_lisitng_ids = list(
        Application.objects.filter(student = profile).values_list('listing_id', flat=True)
    )

    context = {
        'profile'      : profile,
        'applications' : applications,
        'total_applied': total_applied,
        'pending'      : pending,
        'accepted'     : accepted,
        'rejected'     : rejected,
        'recommendations' : recommendations,
        'applied_listing_ids' : applied_lisitng_ids
    }
    return render(request, 'dashboards/student/student.html', context)

# ─────────────────────────────────────────
# REFRESH AI RECOMMENDATIONS
# ─────────────────────────────────────────
@login_required
def refresh_recommendations(request):
    if request.user.role != 'student':
        return redirect('login')

    if request.method != 'POST':
        return redirect('student_dashboard')

    profile = get_object_or_404(StudentProfile, user=request.user)

    # get already applied listing IDs
    applied_ids = Application.objects.filter(
        student=profile
    ).values_list('listing_id', flat=True)

    # get all verified active listings not already applied to
    listings = PlacementListing.objects.filter(
        is_active=True,
        company__status='verified'
    ).exclude(
        id__in=applied_ids
    ).select_related('company', 'state', 'lga')

    if not listings.exists():
        messages.info(request, "No available listings to recommend right now.")
        return redirect('student_dashboard')

    # call Groq
    results = generate_recommendations(profile, listings)

    if not results:
        messages.error(request, "Could not generate recommendations. Please try again.")
        return redirect('student_dashboard')

    # clear old recommendations for this student
    AIRecommendation.objects.filter(student=profile).delete()

    # save new recommendations
    listings_dict = {l.id: l for l in listings}

    for item in results:
        listing = listings_dict.get(item['listing_id'])
        if listing:
            AIRecommendation.objects.create(
                student = profile,
                listing = listing,
                reason  = item['reason'],
                score   = item['score'],
            )

    messages.success(request, f"Generated {len(results)} recommendation(s) for you.")
    return redirect('student_dashboard')

# ─────────────────────────────────────────
# SEARCH PLACEMENTS (Option 3 — location filter)
# ─────────────────────────────────────────
@login_required
def search_placements(request):
    if request.user.role != 'student':
        return redirect('login')

    profile  = get_object_or_404(StudentProfile, user=request.user)
    listings = PlacementListing.objects.filter(
        is_active=True,
        company__status='verified'   # Option 4 — only verified companies
    ).select_related('company', 'state', 'lga')

    # --- filters ---
    state_id  = request.GET.get('state')
    lga_id    = request.GET.get('lga')
    dept      = request.GET.get('department')

    if state_id:
        listings = listings.filter(state_id=state_id)
    if lga_id:
        listings = listings.filter(lga_id=lga_id)
    if dept:
        listings = listings.filter(department_required__icontains=dept)

    # track which listings student already applied to
    applied_listing_ids = Application.objects.filter(
        student=profile
    ).values_list('listing_id', flat=True)

    states = State.objects.all()
    lgas   = LGA.objects.filter(state_id=state_id) if state_id else LGA.objects.none()

    context = {
        'listings'            : listings,
        'states'              : states,
        'lgas'                : lgas,
        'applied_listing_ids' : list(applied_listing_ids),
        'selected_state'      : state_id,
        'selected_lga'        : lga_id,
        'selected_dept'       : dept or '',
        'profile'             : profile,
    }
    return render(request, 'dashboards/student/search.html', context)

# ─────────────────────────────────────────
# APPLY FOR PLACEMENT
# ─────────────────────────────────────────
@login_required
def apply_placement(request, listing_id):
    if request.user.role != 'student':
        return redirect('login')

    profile = get_object_or_404(StudentProfile, user=request.user)
    listing = get_object_or_404(PlacementListing, id=listing_id, is_active=True)

    # check if already applied
    already_applied = Application.objects.filter(student=profile, listing=listing).exists()
    if already_applied:
        messages.warning(request, "You have already applied to this placement.")
        return redirect('search_placements')

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application         = form.save(commit=False)
            application.student = profile
            application.listing = listing
            application.status  = 'pending'
            application.save()
            messages.success(request, f"Application submitted to {listing.company.company_name}!")
            return redirect('student_dashboard')
    else:
        form = ApplicationForm()

    context = {
        'form'   : form,
        'listing': listing,
    }
    return render(request, 'dashboards/student/apply.html', context)


@login_required
def my_profile(request):
    if request.user.role != 'student':
        return redirect('login')

    profile = get_object_or_404(StudentProfile, user=request.user)

    total_applied = Application.objects.filter(student=profile).count()
    pending       = Application.objects.filter(student=profile, status='pending').count()
    accepted      = Application.objects.filter(student=profile, status='accepted').count()
    rejected      = Application.objects.filter(student=profile, status='rejected').count()

    context = {
        'profile'      : profile,
        'total_applied': total_applied,
        'pending'      : pending,
        'accepted'     : accepted,
        'rejected'     : rejected,
    }
    return render(request, 'dashboards/student/myProfile.html', context)

# ─────────────────────────────────────────
# STUDENT RESPOND TO OFFER
# ─────────────────────────────────────────
@login_required
def respond_to_offer(request, app_id):
    if request.user.role != 'student':
        return redirect('login')

    profile     = get_object_or_404(StudentProfile, user=request.user)
    application = get_object_or_404(Application, id=app_id, student=profile)

    # only allow response if status is 'offered'
    if application.status != 'offered':
        messages.error(request, "This offer is no longer available to respond to.")
        return redirect('my_applications')

    if request.method == 'POST':
        decision = request.POST.get('decision')

        if decision == 'accept':
            application.status = 'offer_accepted'
            application.save()

            notify_admin_offer_accepted(application)
            notify_company_offer_response(application)

            messages.success(request, f"You have accepted the placement offer from {application.listing.company.company_name}.")

        elif decision == 'decline':
            application.status = 'offer_declined'
            application.save()

            notify_company_offer_response(application)

            messages.info(request, f"You have declined the placement offer from {application.listing.company.company_name}.")

        else:
            messages.error(request, "Invalid decision.")

    return redirect('my_applications')


@login_required
def my_applications(request):
    if request.user.role != 'student':
        return redirect('login')

    profile = get_object_or_404(StudentProfile, user=request.user)

    status = request.GET.get('status', '')
    applications = Application.objects.filter(
        student=profile
    ).select_related(
        'listing__company',
        'listing__state',
        'listing__lga'
    ).order_by('-applied_at')

    if status:
        applications = applications.filter(status=status)

    total_applied = Application.objects.filter(student=profile).count()
    pending = Application.objects.filter(student=profile, status='pending').count()
    accepted = Application.objects.filter(student=profile, status='offer_accepted').count()
    rejected = Application.objects.filter(student=profile, status='rejected').count()
    offered = Application.objects.filter(student=profile, status='offered').count()

    context = {
        'profile'        : profile,
        'applications'   : applications,
        'total_applied'  : total_applied,
        'pending'        : pending,
        'accepted'       : accepted,
        'rejected'       : rejected,
        'offered'        : offered,
        'selected_status': status,
    }
    return render(request, 'dashboards/student/my_applications.html', context)


@login_required
def company_dashboard(request):
    if request.user.role != 'company':
        return redirect('login')

    profile  = get_object_or_404(CompanyProfile, user=request.user)
    listings = PlacementListing.objects.filter(
        company=profile
    ).prefetch_related('applications').order_by('-created_at')

    # stats
    total_listings     = listings.count()
    active_listings    = listings.filter(is_active=True).count()
    total_applications = Application.objects.filter(listing__company=profile).count()
    pending_apps       = Application.objects.filter(listing__company=profile, status='pending').count()
    accepted_apps      = Application.objects.filter(listing__company=profile, status='accepted').count()

    context = {
        'profile'           : profile,
        'listings'          : listings,
        'total_listings'    : total_listings,
        'active_listings'   : active_listings,
        'total_applications': total_applications,
        'pending_apps'      : pending_apps,
        'accepted_apps'     : accepted_apps
    }
    return render(request, 'dashboards/company/company.html', context)

# ─────────────────────────────────────────
# COMPANY PROFILE
# ─────────────────────────────────────────
@login_required
def company_profile(request):
    if request.user.role != 'company':
        return redirect('login')

    profile = get_object_or_404(CompanyProfile, user=request.user)
    context = {'profile': profile}
    return render(request, 'dashboards/company/company_profile.html', context)

# ─────────────────────────────────────────
# POST NEW LISTING
# ─────────────────────────────────────────
@login_required
def post_listing(request):
    if request.user.role != 'company':
        return redirect('login')

    profile = get_object_or_404(CompanyProfile, user=request.user)

    # block unverified companies from posting
    if not profile.is_verified:
        messages.error(request, "Your account must be verified before posting listings.")
        return redirect('company_dashboard')

    form = PlacementListingForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            listing         = form.save(commit=False)
            listing.company = profile
            listing.save()
            messages.success(request, "Listing posted successfully.")
            return redirect('company_dashboard')
        else:
            messages.error(request, "Please fix the errors below.")

    return render(request, 'dashboards/company/post_listing.html', {'form': form, 'profile' : profile})

# ─────────────────────────────────────────
# EDIT LISTING
# ─────────────────────────────────────────
@login_required
def edit_listing(request, listing_id):
    if request.user.role != 'company':
        return redirect('login')

    profile = get_object_or_404(CompanyProfile, user=request.user)
    listing = get_object_or_404(PlacementListing, id=listing_id, company=profile)
    form    = PlacementListingForm(request.POST or None, instance=listing)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Listing updated successfully.")
            return redirect('company_dashboard')
        else:
            messages.error(request, "Please fix the errors below.")

    return render(request, 'dashboards/company/edit_listing.html', {
        'form'   : form,
        'listing': listing,
        'profile': profile,
    })

# ─────────────────────────────────────────
# DELETE LISTING
# ─────────────────────────────────────────
@login_required
def delete_listing(request, listing_id):
    if request.user.role != 'company':
        return redirect('login')

    profile = get_object_or_404(CompanyProfile, user=request.user)
    listing = get_object_or_404(PlacementListing, id=listing_id, company=profile)

    if request.method == 'POST':
        listing.delete()
        messages.success(request, "Listing deleted.")

    return redirect('company_dashboard')

# ─────────────────────────────────────────
# VIEW APPLICATIONS FOR A LISTING
# ─────────────────────────────────────────
@login_required
def listing_applications(request, listing_id):
    if request.user.role != 'company':
        return redirect('login')

    profile  = get_object_or_404(CompanyProfile, user=request.user)
    listing  = get_object_or_404(PlacementListing, id=listing_id, company=profile)
    applications = Application.objects.filter(
        listing=listing
    ).select_related('student__user').order_by('-applied_at')
    print("Applications : ", applications)
    status = request.GET.get('status', '')
    print("Filter status: ", status)
    if status:
        applications = applications.filter(status=status)

    context = {
        'profile'         : profile,
        'listing'         : listing,
        'applications'    : applications,
        'selected_status' : status,
        'total'           : Application.objects.filter(listing=listing).count(),
        'pending'         : Application.objects.filter(listing=listing, status='pending').count(),
        'accepted'        : Application.objects.filter(listing=listing, status='accepted').count(),
        'rejected'        : Application.objects.filter(listing=listing, status='rejected').count(),
    }
    
    return render(request, 'dashboards/company/listing_applications.html', context)

# ─────────────────────────────────────────
# UPDATE APPLICATION STATUS
# ─────────────────────────────────────────
@login_required
def update_application_status(request, app_id):
    if request.user.role != 'company':
        return redirect('login')

    profile     = get_object_or_404(CompanyProfile, user=request.user)
    application = get_object_or_404(Application, id=app_id, listing__company=profile)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        note       = request.POST.get('company_note', '')

        if new_status in ['pending', 'reviewed', 'offered', 'accepted', 'rejected']:
            application.status = new_status
            application.company_note = note
            application.save()

            notify_student_status_change(application)

            messages.success(request, f"Application status updated to {new_status}.")

    return redirect('listing_applications', listing_id=application.listing.id)

# ─────────────────────────────────────────
# TOGGLE LISTING ACTIVE/INACTIVE
# ─────────────────────────────────────────
@login_required
def toggle_listing(request, listing_id):
    if request.user.role != 'company':
        return redirect('login')

    profile = get_object_or_404(CompanyProfile, user=request.user)
    listing = get_object_or_404(PlacementListing, id=listing_id, company=profile)
    listing.is_active = not listing.is_active
    listing.save()
    status = "activated" if listing.is_active else "deactivated"
    messages.success(request, f"Listing {status} successfully.")
    return redirect('company_dashboard')


@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        messages.error(request, "You do not have permission to access the admin panel.")
        if request.user.role == 'student':
            return redirect('student_dashboard')
        elif request.user.role == 'company':
            return redirect('company_dashboard')
        return redirect('login')

    # stats
    total_students   = StudentProfile.objects.count()
    total_companies  = CompanyProfile.objects.count()
    verified_cos     = CompanyProfile.objects.filter(status='verified').count()
    pending_cos      = CompanyProfile.objects.filter(status='pending').count()
    rejected_cos     = CompanyProfile.objects.filter(status='rejected').count()
    total_listings   = PlacementListing.objects.count()
    active_listings  = PlacementListing.objects.filter(is_active=True).count()
    total_apps       = Application.objects.count()
    accepted_apps    = Application.objects.filter(status='accepted').count()
    pending_apps     = Application.objects.filter(status='pending').count()

    recent_students  = StudentProfile.objects.select_related('user').order_by('-created_at')[:6]
    recent_companies = CompanyProfile.objects.select_related('user').order_by('-created_at')[:6]

    # recent activity
    recent_students  = StudentProfile.objects.select_related('user').order_by('-created_at')[:5]
    recent_companies = CompanyProfile.objects.select_related('user').order_by('-created_at')[:5]

    context = {
        'total_students'  : total_students,
        'total_companies' : total_companies,
        'verified_cos'    : verified_cos,
        'pending_cos'     : pending_cos,
        'rejected_cos'    : rejected_cos,
        'total_listings'  : total_listings,
        'active_listings' : active_listings,
        'total_apps'      : total_apps,
        'accepted_apps'   : accepted_apps,
        'pending_apps'    : pending_apps,
        'recent_students' : recent_students,
        'recent_companies': recent_companies,
    }

    return render(request, 'dashboards/admin/admin.html', context)

# ─────────────────────────────────────────
# PENDING COMPANIES — Option 4
# ─────────────────────────────────────────
@login_required
def pending_companies(request):
    if request.user.role != 'admin':
        return redirect('login')

    companies = CompanyProfile.objects.filter(
        status='pending'
    ).select_related('user', 'state', 'lga').order_by('-created_at')

    return render(request, 'dashboards/admin/pending_companies.html', {'companies': companies, 'count' : companies.count(), 'pending_cos': CompanyProfile.objects.filter(status='pending').count(),})

# ─────────────────────────────────────────
# VERIFY / REJECT COMPANY — Option 4
# ─────────────────────────────────────────
@login_required
def verify_company(request, company_id):
    if request.user.role != 'admin':
        return redirect('login')

    company = get_object_or_404(CompanyProfile, id=company_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'verify':
            company.status      = 'verified'
            company.verified_at = timezone.now()
            company.save()
            messages.success(request, f"{company.company_name} has been verified.")

        elif action == 'reject':
            company.status = 'rejected'
            company.save()
            messages.warning(request, f"{company.company_name} has been rejected.")

    return redirect('pending_companies')


# ─────────────────────────────────────────
# ADMIN FULL FUNCTIONS
# ─────────────────────────────────────────

# ─────────────────────────────────────────
# ALL COMPANIES
# ─────────────────────────────────────────
@login_required
def all_companies(request):
    if request.user.role != 'admin':
        return redirect('login')

    status    = request.GET.get('status', '')
    search    = request.GET.get('search', '')
    companies = CompanyProfile.objects.select_related(
        'user', 'state', 'lga'
    ).order_by('-created_at')

    if status:
        companies = companies.filter(status=status)
    if search:
            companies = companies.filter(company_name__icontains=search)
    context = {
        'companies'      : companies,
        'selected_status': status,
        'search' : search,
        'total' : companies.count(),
        'pending_cos': CompanyProfile.objects.filter(status='pending').count(),
    }
    return render(request, 'dashboards/admin/all_companies.html', context)


# ─────────────────────────────────────────
# ALL STUDENTS
# ─────────────────────────────────────────
@login_required
def all_students(request):
    if request.user.role != 'admin':
        return redirect('login')
    search   = request.GET.get('search', '')
    dept     = request.GET.get('department', '') 
    students = StudentProfile.objects.select_related(
        'user', 'preferred_state', 'preferred_lga'
    ).order_by('-created_at')

    if search:
            students = students.filter(
                user__first_name__icontains=search
            ) | students.filter(
                user__last_name__icontains=search
            ) | students.filter(
                matric_number__icontains=search
            )
    if dept:
            students = students.filter(department__icontains=dept)

    context = {
        'students': students,
        'search'  : search,
        'dept'    : dept,
        'total'   : students.count(),
        'pending_cos': CompanyProfile.objects.filter(status='pending').count(),
    }

    return render(request, 'dashboards/admin/all_students.html', context)

@login_required
def admin_student_detail(request, student_id):
    if request.user.role != 'admin':
        return redirect('login')

    student      = get_object_or_404(StudentProfile, id=student_id)
    applications = Application.objects.filter(
        student=student
    ).select_related('listing__company', 'listing__state', 'listing__lga').order_by('-applied_at')

    context = {
        'student'         : student,
        'applications'    : applications,
        'total_applied'   : applications.count(),
        'accepted'        : applications.filter(status='offer_accepted').count(),
        'pending'         : applications.filter(status='pending').count(),
        'rejected'        : applications.filter(status='rejected').count(),
        'pending_cos'     : CompanyProfile.objects.filter(status='pending').count(),
    }
    return render(request, 'dashboards/admin/student_detail.html', context)

@login_required
def admin_company_detail(request, company_id):
    if request.user.role != 'admin':
        return redirect('login')

    company  = get_object_or_404(CompanyProfile, id=company_id)
    listings = PlacementListing.objects.filter(
        company=company
    ).prefetch_related('applications').order_by('-created_at')

    total_listings     = listings.count()
    active_listings    = listings.filter(is_active=True).count()
    total_applications = Application.objects.filter(listing__company=company).count()
    accepted           = Application.objects.filter(listing__company=company, status='offer_accepted').count()

    context = {
        'company'           : company,
        'listings'          : listings,
        'total_listings'    : total_listings,
        'active_listings'   : active_listings,
        'total_applications': total_applications,
        'accepted'          : accepted,
        'pending_cos'       : CompanyProfile.objects.filter(status='pending').count(),
    }
    return render(request, 'dashboards/admin/company_detail.html', context)

# ─────────────────────────────────────────
# ALL APPLICATIONS
# ─────────────────────────────────────────
@login_required
def all_applications(request):
    if request.user.role != 'admin':
        return redirect('login')

    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    apps   = Application.objects.select_related(
        'student__user', 'listing__company'
    ).order_by('-applied_at')

    if status:
        apps = apps.filter(status=status)

    if search:
        apps = apps.filter(
            student__user__first_name__icontains=search
        ) | apps.filter(
            listing__company__company_name__icontains=search
        )

    context = {
        'applications'   : apps,
        'selected_status': status,
        'search'         : search,
        'total'          : apps.count(),
        'pending_cos': CompanyProfile.objects.filter(status='pending').count(),
    }
    return render(request, 'dashboards/admin/all_applications.html', context)

# ─────────────────────────────────────────
# ADMIN REGISTER COMPANY
# ─────────────────────────────────────────
@login_required
def admin_register_company(request):
    if request.user.role != 'admin':
        return redirect('login')

    form        = AdminRegisterCompanyForm(request.POST or None)
    credentials = None  # shown after successful creation

    if request.method == 'POST':
        if form.is_valid():
            # auto-generate username and password
            base_username = form.cleaned_data['company_name'].lower().replace(' ', '_')[:15]
            username      = base_username
            counter       = 1

            # ensure username is unique
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            password = generate_password_name(form.cleaned_data['company_name'])
 
            # create user
            user = User.objects.create_user(
                username   = username,
                password   = password,
                email      = form.cleaned_data['email'],
                first_name = form.cleaned_data['first_name'],
                last_name  = form.cleaned_data['last_name'],
                phone      = form.cleaned_data['phone'],
                role       = 'company',
            )

            # create company profile — auto verified since admin is registering
            CompanyProfile.objects.create(
                user         = user,
                company_name = form.cleaned_data['company_name'],
                industry     = form.cleaned_data['industry'],
                description  = form.cleaned_data['description'],
                address      = form.cleaned_data['address'],
                website      = form.cleaned_data.get('website', ''),
                state        = form.cleaned_data['state'],
                lga          = form.cleaned_data['lga'],
                status       = 'verified',
                verified_at  = timezone.now(),
            )

            credentials = {
                'company_name': form.cleaned_data['company_name'],
                'username'    : username,
                'password'    : password,
                'email'       : form.cleaned_data['email'],
            }

            messages.success(request, f"Company '{form.cleaned_data['company_name']}' registered successfully.")
            form = AdminRegisterCompanyForm()  # reset form after success

        else:
            messages.error(request, "Please fix the errors below.")

    return render(request, 'dashboards/admin/register_company.html', {
        'form'       : form,
        'credentials': credentials,
    })

# core/views.py
@login_required
def admin_reset_password(request, user_id):
    if request.user.role != 'admin':
        return redirect('login')

    target_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        if len(new_password) >= 6:
            target_user.set_password(new_password)
            target_user.save()
            messages.success(request, f"Password for {target_user.get_full_name()} has been reset.")
        else:
            messages.error(request, "Password must be at least 6 characters.")

    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

# ─────────────────────────────────────────
# ADMIN DELETE STUDENT
# ─────────────────────────────────────────
@login_required
def admin_delete_student(request, student_id):
    if request.user.role != 'admin':
        return redirect('login')

    profile = get_object_or_404(StudentProfile, id=student_id)

    if request.method == 'POST':
        name = profile.user.get_full_name()
        profile.user.delete()  # cascades to StudentProfile + Applications
        messages.success(request, f"Student '{name}' has been deleted.")

    return redirect('all_students')


# ─────────────────────────────────────────
# ADMIN DELETE COMPANY
# ─────────────────────────────────────────
@login_required
def admin_delete_company(request, company_id):
    if request.user.role != 'admin':
        return redirect('login')

    company = get_object_or_404(CompanyProfile, id=company_id)

    if request.method == 'POST':
        name = company.company_name
        company.user.delete()  # cascades to CompanyProfile + Listings + Applications
        messages.success(request, f"Company '{name}' has been deleted.")

    return redirect('all_companies')


# ─────────────────────────────────────────
# ADMIN — MANAGE ADMIN ACCOUNTS
# ─────────────────────────────────────────
@login_required
def manage_admins(request):
    if request.user.role != 'admin':
        return redirect('login')

    admins = User.objects.filter(role='admin').order_by('date_joined')

    context = {
        'admins'     : admins,
        'pending_cos': CompanyProfile.objects.filter(status='pending').count(),
    }
    return render(request, 'dashboards/admin/manage_admins.html', context)


@login_required
def create_admin_view(request):
    if request.user.role != 'admin':
        return redirect('login')

    if request.method == 'POST':
        username   = request.POST.get('username', '').strip()
        email      = request.POST.get('email', '').strip()
        password   = request.POST.get('password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()

        if not all([username, email, password, first_name]):
            messages.error(request, "All fields are required.")
            return redirect('manage_admins')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken.")
            return redirect('manage_admins')

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect('manage_admins')

        User.objects.create_superuser(
            username   = username,
            email      = email,
            password   = password,
            first_name = first_name,
            last_name  = last_name,
            role       = 'admin',
        )
        messages.success(request, f"Admin '{username}' created successfully.")

    return redirect('manage_admins')


@login_required
def delete_admin(request, admin_id):
    if request.user.role != 'admin':
        return redirect('login')

    # prevent self-deletion
    if request.user.id == admin_id:
        messages.error(request, "You cannot delete your own account.")
        return redirect('manage_admins')

    admin = get_object_or_404(User, id=admin_id, role='admin')

    if request.method == 'POST':
        name = admin.get_full_name() or admin.username
        admin.delete()
        messages.success(request, f"Admin '{name}' deleted.")

    return redirect('manage_admins')


@login_required
def change_admin_password(request, admin_id):
    if request.user.role != 'admin':
        return redirect('login')

    admin = get_object_or_404(User, id=admin_id, role='admin')

    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()

        if len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect('manage_admins')

        admin.set_password(new_password)
        admin.save()

        # if changing own password, keep logged in
        if request.user.id == admin_id:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, admin)
            messages.success(request, "Your password has been updated.")
        else:
            messages.success(request, f"Password for '{admin.username}' updated.")

    return redirect('manage_admins')