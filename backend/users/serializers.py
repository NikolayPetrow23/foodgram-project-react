from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import Follow, User


class SignUpUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(
            **validated_data,
            password=password
        )
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password', None)
        return representation


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        if not user.is_anonymous:
            if Follow.objects.filter(user=user, author=obj).exists():
                return True
            return False
        return None


class CustomUserResetPassword(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True)
    current_password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = (
            'new_password',
            'current_password'
        )

    def validate(self, attrs):
        user = self.context["request"].user or self.user
        assert user is not None

        try:
            validate_password(attrs["new_password"], user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)}
            )
        return super().validate(attrs)

    def validate_current_password(self, value):
        is_password_valid = self.context["request"].user.check_password(value)
        if is_password_valid:
            return value
        else:
            self.fail("invalid_password")


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        print(self.context)
        # follow = self.context["follow"]
        if not user.is_anonymous:
            if Follow.objects.filter(user=user, author=obj.author).exists():
                return True
            return False
        return None

    def get_recipes(self, obj):
        from app.serializers import RecipeFavoriteSerializer
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        recipes = (
            obj.author.recipes_user.all()[: int(limit)]
            if limit
            else obj.author.recipes_user.all()
        )

        return RecipeFavoriteSerializer(
            recipes,
            many=True,
            context=self.context
        ).data

    @classmethod
    def get_recipes_count(cls, obj):
        return obj.author.recipes_user.all().count()
