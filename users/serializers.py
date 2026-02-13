from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    


    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password', 'confirm_password', 'email', 'phone_number', 'address')

    def validate(self, attrs):
    
        if attrs.get('password') != attrs.get('confirm_password'):
            raise ValidationError({'confirm_password':'Paroller saykes kelmedi!'})
        
        attrs.pop('confirm_password', None)
        return attrs
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
        


    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'address']
        read_only_fields = ['id', 'phone_number']

class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise ValidationError({'confirm_password': 'Paroller sáykes kelmeydi!'})
        return attrs
    


