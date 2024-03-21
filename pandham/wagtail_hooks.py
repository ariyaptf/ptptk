from django import forms
from django.utils.translation import gettext_lazy as _
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register
)
from .models import (
    PandhamTargetGroup,
    PandhamTarget,
    BookInventory,
    PandhamStock,
    InventoryTransaction,
    Propagation,
    RequestPandham,
)

class PandhamTargetGroupAdmin(ModelAdmin):
    model = PandhamTargetGroup
    menu_label = _("Target Group",)
    menu_icon = "group"
    menu_order = 100
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("name", "priority",)
    search_fields = ("name",)

class PandhamTargetAdmin(ModelAdmin):
    model = PandhamTarget
    menu_label = _("Target",)
    menu_icon = "user"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("name", "requested_books", "group",)
    search_fields = ("name",)
    list_filter = ("pandham_target_group",)

class BookInventoryAdmin(ModelAdmin):
    model = BookInventory
    menu_label = _("Inventory",)
    menu_icon = "list-ul"
    menu_order = 300
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("sequence_order", "book_name", "current_stock", "price",)
    ordering = ("sequence_order",)
    search_fields = ("book_name",)
    list_filter = ("is_available",)

class PandhamStockAdmin(ModelAdmin):
    model = PandhamStock
    menu_label = _("Pandham Stock",)
    menu_icon = "list-ul"
    menu_order = 400
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("book_inventory", "current_stock",)
    search_fields = ("book_inventory__book_name",)
    list_filter = ("book_inventory",)


class InventoryTransactionAdmin(ModelAdmin):
    model = InventoryTransaction
    menu_label = _("Transaction",)
    menu_icon = "list-ul"
    menu_order = 500
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("book_inventory", "quantity", "transaction_type",)
    ordering = ("-created_at",)
    search_fields = ("book_inventory__book_name",)
    list_filter = ("transaction_type", "book_inventory__book_name",)

class PropagationAdmin(ModelAdmin):
    model = Propagation
    menu_label = _("Propagation",)
    menu_icon = "list-ul"
    menu_order = 600
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("book_inventory", "number_of_books",)
    search_fields = ("book_inventory__name",)
    list_filter = ("book_inventory", "target_groups",)

class RequestPandhamAdmin(ModelAdmin):
    model = RequestPandham
    menu_label = _("Request Pandham",)
    menu_icon = "list-ul"
    menu_order = 700
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("book_inventory", "number_of_books", "is_waiting")
    search_fields = ("book_inventory__name",)
    list_filter = ("book_inventory", "is_waiting",  "recipient_category",)

class PandhamAdminGroup(ModelAdminGroup):
    menu_label = _("Pandham",)
    menu_icon = "view"
    menu_order = 1500
    items = (
        PandhamTargetGroupAdmin,
        PandhamTargetAdmin,
        BookInventoryAdmin,
        PandhamStockAdmin,
        InventoryTransactionAdmin,
        PropagationAdmin,
        RequestPandhamAdmin,
    )

modeladmin_register(PandhamAdminGroup)

