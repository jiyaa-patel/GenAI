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
            return Response({"error": "Invalid credentials"}, status=401)
        
# Google API  
class GoogleLoginView(APIView):
  def post(self,request):
    token = request.data.get("token") # frontend sends Google access token

    try:
      # Get user info from Google using access token
      import requests
      user_info_response = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {token}'}
      )
      user_info = user_info_response.json()

      if 'error' in user_info:
        return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)

      email = user_info['email']
      name = user_info.get('name', email.split('@')[0])

      # If user doesn't exist, create one
      user, created = User.objects.get_or_create(
        email=email,
        defaults={
          "display_name": name,
        }
      )
      
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
        return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)