"""
Authentication views for the collaborative worldbuilding application.
Handles user registration, profile management, and JWT token operations.
"""
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from ..serializers import (
    UserRegistrationSerializer, 
    UserProfileSerializer, 
    UserSerializer,
    PasswordChangeSerializer
)
from ..models import UserProfile


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes user profile information.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        
        # Add profile information if it exists
        try:
            profile = user.worldbuilding_profile
            token['contribution_count'] = profile.contribution_count
            token['worlds_created'] = profile.worlds_created
        except UserProfile.DoesNotExist:
            token['contribution_count'] = 0
            token['worlds_created'] = 0
        
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user profile data to response
        try:
            profile = self.user.worldbuilding_profile
            data['user'] = {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'profile': UserProfileSerializer(profile).data
            }
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = UserProfile.objects.create(user=self.user)
            data['user'] = {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'profile': UserProfileSerializer(profile).data
            }
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view with enhanced user data.
    """
    serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationView(CreateAPIView):
    """
    API view for user registration.
    Creates a new user account with associated profile.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        # Get user profile data
        profile = user.worldbuilding_profile
        
        return Response({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'profile': UserProfileSerializer(profile).data
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class UserProfileView(RetrieveUpdateAPIView):
    """
    API view for retrieving and updating user profile.
    Users can only access their own profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Get the current user's profile."""
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def update(self, request, *args, **kwargs):
        """Update user profile with validation."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Update user fields if provided
        user_data = {}
        if 'first_name' in request.data:
            user_data['first_name'] = request.data['first_name']
        if 'last_name' in request.data:
            user_data['last_name'] = request.data['last_name']
        
        if user_data:
            for field, value in user_data.items():
                setattr(request.user, field, value)
            request.user.save()
        
        # Update profile fields
        profile_data = {}
        if 'bio' in request.data:
            profile_data['bio'] = request.data['bio']
        if 'preferred_content_types' in request.data:
            profile_data['preferred_content_types'] = request.data['preferred_content_types']
        
        if profile_data:
            for field, value in profile_data.items():
                setattr(instance, field, value)
            instance.save()
        
        return Response(serializer.data)


class PasswordChangeView(APIView):
    """
    API view for changing user password.
    Requires authentication and current password verification.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    API view for user logout.
    Blacklists the refresh token to prevent reuse.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({
                    'message': 'Successfully logged out'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_info(request):
    """
    API endpoint to get current user information.
    Returns user data with profile information.
    """
    try:
        profile = request.user.worldbuilding_profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    return Response({
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'date_joined': request.user.date_joined,
            'profile': UserProfileSerializer(profile).data
        }
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_token(request):
    """
    API endpoint to verify JWT token validity.
    Returns user information if token is valid.
    """
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    
    try:
        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({
                'error': 'Authorization header missing or invalid'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]
        
        # Validate token
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
        
        # Return user information
        try:
            profile = user.worldbuilding_profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
        
        return Response({
            'valid': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'profile': UserProfileSerializer(profile).data
            }
        })
        
    except (InvalidToken, TokenError) as e:
        return Response({
            'valid': False,
            'error': str(e)
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({
            'valid': False,
            'error': 'Token verification failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)