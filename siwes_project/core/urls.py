from django.urls import path
from . import views

urlpatterns = [
    path('register/student/', views.register_student, name='register_student'),
    path('register/company/', views.register_company, name='register_company'),
    path('login/',            views.login_view,        name='login'),
    path('logout/',           views.logout_view,       name='logout'),
    path('ajax/load-lgas/',   views.load_lgas,         name='load_lgas'),

    path('student/dashboard/',          views.student_dashboard,  name='student_dashboard'),
    path('student/search/',             views.search_placements,  name='search_placements'),
    path('student/profile/', views.my_profile, name='my_profile'),
    path('student/profile/edit/',  views.edit_student_profile, name='edit_student_profile'),
    path('student/applications/', views.my_applications, name='my_applications'),
    path('student/apply/<int:listing_id>/', views.apply_placement, name='apply_placement'),
    path('student/recommendations/refresh/', views.refresh_recommendations, name='refresh_recommendations'),
    path('student/application/<int:app_id>/respond/', views.respond_to_offer, name='respond_to_offer'),

    path('company/dashboard/',                              views.company_dashboard,          name='company_dashboard'),
    path('company/profile/',                                views.company_profile,            name='company_profile'),
    path('company/profile/edit/',  views.edit_company_profile, name='edit_company_profile'),
    path('company/post-listing/',                           views.post_listing,               name='post_listing'),
    path('company/listing/<int:listing_id>/edit/',          views.edit_listing,               name='edit_listing'),
    path('company/listing/<int:listing_id>/delete/',        views.delete_listing,             name='delete_listing'),
    path('company/listing/<int:listing_id>/toggle/',        views.toggle_listing,             name='toggle_listing'),
    path('company/listing/<int:listing_id>/applications/',  views.listing_applications,       name='listing_applications'),
    path('company/application/<int:app_id>/update/',        views.update_application_status,  name='update_application_status'),
    
    path('admin-panel/dashboard/',   views.admin_dashboard,   name='admin_dashboard'),
    path('admin-panel/pending-companies/',        views.pending_companies, name='pending_companies'),
    path('admin-panel/verify/<int:company_id>/',  views.verify_company,    name='verify_company'),
    path('admin-panel/companies/',                views.all_companies,     name='all_companies'),
    path('admin-panel/students/',                 views.all_students,      name='all_students'),
    path('admin-panel/applications/',             views.all_applications,  name='all_applications'),
    path('admin-panel/register-company/',              views.admin_register_company, name='admin_register_company'),
    path('admin-panel/delete-student/<int:student_id>/', views.admin_delete_student, name='admin_delete_student'),
    path('admin-panel/delete-company/<int:company_id>/', views.admin_delete_company, name='admin_delete_company'),
    path('admin-panel/students/<int:student_id>/', views.admin_student_detail, name='admin_student_detail'),
    path('admin-panel/companies/<int:company_id>/', views.admin_company_detail, name='admin_company_detail'),
    path('admin-panel/reset-password/<int:user_id>/', views.admin_reset_password, name='admin_reset_password'),

    path('admin-panel/admins/',                              views.manage_admins,          name='manage_admins'),
    path('admin-panel/admins/create/',                       views.create_admin_view,      name='create_admin_view'),
    path('admin-panel/admins/<int:admin_id>/delete/',        views.delete_admin,           name='delete_admin'),
    path('admin-panel/admins/<int:admin_id>/change-password/', views.change_admin_password, name='change_admin_password'),

    path('setup/',                views.setup_view,          name='setup'),
    path('setup/migrate/',        views.setup_migrate,       name='setup_migrate'),
    path('setup/seed-nigeria/',   views.setup_seed_nigeria,  name='setup_seed_nigeria'),
    path('setup/seed-companies/', views.setup_seed_companies,name='setup_seed_companies'),
    path('setup/create-admin/',   views.setup_create_admin,  name='setup_create_admin'),
]