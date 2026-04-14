from django.contrib import admin
from .models import Ticket, Commentaire, HistoriqueStatut


class CommentaireInline(admin.TabularInline):
    model = Commentaire
    extra = 0
    readonly_fields = ['auteur', 'date']


class HistoriqueInline(admin.TabularInline):
    model = HistoriqueStatut
    extra = 0
    readonly_fields = ['ancien_statut', 'nouveau_statut', 'date_changement', 'modifie_par']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display  = ['titre', 'type_ticket', 'statut', 'priorite', 'auteur', 'assigne_a', 'date_creation']
    list_filter   = ['statut', 'priorite', 'type_ticket']
    search_fields = ['titre', 'description']
    inlines       = [CommentaireInline, HistoriqueInline]


@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'auteur', 'date']


@admin.register(HistoriqueStatut)
class HistoriqueStatutAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'ancien_statut', 'nouveau_statut', 'date_changement', 'modifie_par']