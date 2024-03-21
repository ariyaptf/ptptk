from django.urls import path
from . import views

urlpatterns = [
    path('resend-otp/', views.ResendOTP, name='resend_otp'),
    # request pandham
    path('request-pandham/<int:book_id>/', views.RequestPandhamView.as_view(), name='request_pandham'),
    path('request-pandham-verify-otp/', views.RequestPandhamVerifyOTPView.as_view(), name='request_pandham_verify_otp'),
    path('request-pandham-success/<int:request_pandham_id>/', views.RequestPandhamSuccessView.as_view(), name='request_pandham_success'),
    # contribute
    path('contribute-pandham/<int:book_id>/', views.ContributePandhamView.as_view(), name='contribute_pandham'),
    path('contribute-pandham-verify-otp/', views.ContributePandhamVerifyOTPView.as_view(), name='contribute_pandham_verify_otp'),
    path('contribute-pandham-success/<int:propagation_id>/', views.ContributePandhamSuccessView.as_view(), name='contribute_pandham_success'),
]
