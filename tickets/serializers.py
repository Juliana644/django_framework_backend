from rest_framework import serializers
from .models import Ticket, Commentaire, HistoriqueStatut
from accounts.models import CustomUser


class UserLightSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email', 'role']

    def get_full_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else obj.email

class CommentaireSerializer(serializers.ModelSerializer):
    auteur = UserLightSerializer(read_only=True)

    class Meta:
        model = Commentaire
        fields = ['id', 'auteur', 'contenu', 'date']
        read_only_fields = ['auteur', 'date']


class HistoriqueStatutSerializer(serializers.ModelSerializer):
    modifie_par = UserLightSerializer(read_only=True)

    class Meta:
        model = HistoriqueStatut
        fields = ['id', 'ancien_statut', 'nouveau_statut', 'date_changement', 'modifie_par']


class TicketSerializer(serializers.ModelSerializer):
    auteur      = UserLightSerializer(read_only=True)
    assigne_a   = UserLightSerializer(read_only=True)
    commentaires = CommentaireSerializer(many=True, read_only=True)
    historique  = HistoriqueStatutSerializer(many=True, read_only=True)
    assigne_a_id = serializers.PrimaryKeyRelatedField(
        source='assigne_a',
        queryset=CustomUser.objects.filter(role='TECHNICIEN'),
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Ticket
        fields = [
            'id', 'titre', 'description', 'type_ticket',
            'statut', 'priorite', 'auteur', 'assigne_a',
            'assigne_a_id', 'date_creation',
            'date_modification', 'date_resolution',
            'commentaires', 'historique',
        ]
        read_only_fields = ['auteur', 'date_creation', 'date_modification']

    def create(self, validated_data):
        validated_data['auteur'] = self.context['request'].user
        return super().create(validated_data)


class TicketListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes (sans commentaires)."""
    auteur    = UserLightSerializer(read_only=True)
    assigne_a = UserLightSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'titre', 'type_ticket', 'statut',
            'priorite', 'auteur', 'assigne_a', 'date_creation'
        ]