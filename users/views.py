from rest_framework import serializers 
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .serializers import RegisterSerializer, UserProfileSerializer, SetPasswordSerializer
from .models import User


#Registratsiya
@extend_schema(tags=['Registeration'])
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

#User Profil
@extend_schema(tags=['User Account'])
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch']

    def get_object(self):
        return self.request.user

#Password almastırıw
@extend_schema(request=SetPasswordSerializer,
        responses={200: serializers.DictField()},tags=['User Parol'])
class SetPasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Parol tabıslı ózgertildi!'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    