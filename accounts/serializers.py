from rest_framework import serializers
from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'first_name',
            'last_name', 'telephone', 'role', 'password'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'first_name',
            'last_name', 'full_name', 'telephone', 'role'
        ]

    def get_full_name(self, obj):
        # Retourne email si pas de nom renseigné
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else obj.email
    
class UserLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email', 'role']