from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q

from .models import Ticket, Commentaire, HistoriqueStatut
from .serializers import (
    TicketSerializer, TicketListSerializer, CommentaireSerializer
)
from .permissions import IsAuteurOrReadOnly, IsTechnicienOrAdmin,IsAdminRole


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related(
        'auteur', 'assigne_a'
    ).prefetch_related('commentaires', 'historique')
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields  = ['statut', 'priorite', 'type_ticket', 'assigne_a']
    search_fields     = ['titre', 'description']
    ordering_fields   = ['date_creation', 'priorite', 'statut']

    def get_serializer_class(self):
        if self.action == 'list':
            return TicketListSerializer
        return TicketSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'CITOYEN':
            qs = Ticket.objects.filter(auteur=user).select_related(
                'auteur', 'assigne_a'
            ).prefetch_related('commentaires', 'historique')
            return qs
        if user.role == 'TECHNICIEN':
            return Ticket.objects.filter(
                Q(assigne_a=user) | Q(auteur=user)
            ).select_related('auteur', 'assigne_a').prefetch_related(
                'commentaires', 'historique'
            )
        return Ticket.objects.all().select_related(
            'auteur', 'assigne_a'
        ).prefetch_related('commentaires', 'historique')

    @action(detail=True, methods=['patch'],
            permission_classes=[IsTechnicienOrAdmin])
    def changer_statut(self, request, pk=None):
        ticket = self.get_object()
        nouveau_statut = request.data.get('statut')
        if nouveau_statut not in dict(Ticket.Statut.choices):
            return Response(
                {'erreur': 'Statut invalide.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ancien_statut = ticket.statut
        ticket.statut = nouveau_statut
        if nouveau_statut == Ticket.Statut.RESOLU:
            ticket.date_resolution = timezone.now()
        ticket.save()
        HistoriqueStatut.objects.create(
            ticket=ticket,
            ancien_statut=ancien_statut,
            nouveau_statut=nouveau_statut,
            modifie_par=request.user,
        )
        return Response(TicketSerializer(ticket, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def commenter(self, request, pk=None):
        ticket = self.get_object()
        serializer = CommentaireSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ticket=ticket, auteur=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'],
            permission_classes=[IsAdminRole])
    def assigner(self, request, pk=None):
        ticket = self.get_object()
        technicien_id = request.data.get('technicien_id')
        try:
            from accounts.models import CustomUser
            tech = CustomUser.objects.get(id=technicien_id, role='TECHNICIEN')
            ticket.assigne_a = tech
            ticket.statut = Ticket.Statut.EN_COURS
            ticket.save()
            return Response(TicketSerializer(ticket, context={'request': request}).data)
        except CustomUser.DoesNotExist:
            return Response(
                {'erreur': 'Technicien introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )
    @action(detail=False, methods=['get'],
        permission_classes=[IsAuthenticated])
    def statistiques(self, request):
        """GET /api/tickets/statistiques/"""
        from accounts.models import CustomUser
        from django.db.models import Count

        stats_statut = dict(
            Ticket.objects.values_list('statut')
                .annotate(total=Count('id'))
                .values_list('statut', 'total')
        )
        stats_technicien = list(
            Ticket.objects.filter(assigne_a__isnull=False)
                .values('assigne_a__first_name', 'assigne_a__last_name')
                .annotate(total=Count('id'))
                .order_by('-total')
        )
        total = Ticket.objects.count()

        return Response({
            'total':            total,
            'par_statut':       stats_statut,
            'par_technicien':   stats_technicien,
        })