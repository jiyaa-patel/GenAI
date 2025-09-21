from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.contrib.auth.hashers import make_password
import requests


User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_users(request):
  users = User.objects.all().values('email', 'display_name')
  return Response(list(users))

class RegisterView(generics.CreateAPIView):
  queryset = User.objects.all()
  permission_classes = [AllowAny]
  def post(self, request, *args, **kargs):
    email = request.data.get("email")
    display_name = request.data.get("display_name")
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(email=email, password=password, display_name=display_name)
    
    # Generate JWT tokens for the new user
    refresh = RefreshToken.for_user(user)
    return Response({
        "message": "User registered successfully",
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "email": user.email,
        "display_name": getattr(user, 'display_name', None) or user.email
    }, status=status.HTTP_201_CREATED)

class ProtectedView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self,request):
    return Response({"message": f"Welcome {getattr(request.user, 'display_name', None) or request.user.email}, you are logged in!"})

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class ManualLoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=400)

        # Check if user exists first
        try:
            user_exists = User.objects.filter(email=email).exists()
        except Exception:
            user_exists = False

        # For custom USERNAME_FIELD=email, pass username=email
        user = authenticate(username=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "display_name": getattr(user, 'display_name', None) or user.email,
                "email": user.email
            })
        else:
            if not user_exists:
                return Response({"error": "No account found with this email address"}, status=401)
            else:
                return Response({"error": "Incorrect password"}, status=401)
        
# Google API  
class GoogleLoginView(APIView):
  def post(self,request):
    print(f"Google login request data: {request.data}")
    token = request.data.get("token") # frontend sends Google access token

    if not token:
      print("No token provided")
      return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
      # Get user info from Google using access token
      import requests
      print(f"Getting user info with token: {token[:50]}...")
      user_info_response = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {token}'}
      )
      
      print(f"Google response status: {user_info_response.status_code}")
      print(f"Google response: {user_info_response.text}")
      
      if user_info_response.status_code != 200:
        return Response({"error": f"Google token verification failed: {user_info_response.text}"}, status=status.HTTP_400_BAD_REQUEST)
      
      user_info = user_info_response.json()
      print(f"User info from Google: {user_info}")

      if 'error' in user_info:
        return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)

      email = user_info.get('email')
      name = user_info.get('name', email.split('@')[0] if email else 'User')

      if not email:
        return Response({"error": "Email not found in token"}, status=status.HTTP_400_BAD_REQUEST)

      # If user doesn't exist, create one
      user, created = User.objects.get_or_create(
        email=email,
        defaults={
          "display_name": name,
        }
      )
      
      print(f"User created/found: {user.email}, created: {created}")
      
      # Issue JWT tokens
      refresh = RefreshToken.for_user(user)
      return Response({
          "message": "Google login successful",
          "access": str(refresh.access_token),
          "refresh": str(refresh),
          "display_name": user.display_name,
          "email": user.email,
          "name": name
      })

    except Exception as e:
        print(f"Google login error: {e}")
        import traceback
        traceback.print_exc()
        return Response({"error": f"Google login failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

# Simple in-memory token storage (use Redis or database in production)
reset_tokens = {}

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        
        if not email:
            return Response({"error": "Email is required"}, status=400)
        
        try:
            user = User.objects.get(email=email)
            # Generate a simple reset token
            import secrets
            reset_token = secrets.token_urlsafe(32)
            
            # Store token in memory (simplified approach)
            reset_tokens[email] = reset_token
            
            return Response({
                "message": "Password reset instructions sent to your email",
                "reset_token": reset_token  # Remove this in production
            })
            
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            return Response({
                "message": "If an account with this email exists, password reset instructions have been sent"
            })

class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        
        if not all([email, token, new_password]):
            return Response({"error": "Email, token, and new password are required"}, status=400)
        
        # Verify token from memory storage
        stored_token = reset_tokens.get(email)
        
        if not stored_token:
            return Response({"error": "No reset token found. Please request a new password reset."}, status=400)
        
        if stored_token != token:
            return Response({"error": "Invalid reset token"}, status=400)
        
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            # Clear the reset token
            del reset_tokens[email]
            
            return Response({"message": "Password reset successful"})
            
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def test_django(request):
    """Simple test endpoint to verify Django is working"""
    from datetime import datetime
    return Response({
        'message': 'Django server is working!',
        'timestamp': str(datetime.now())
    })