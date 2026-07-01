from django.contrib import admin
from .models import Group, GroupMember


class GroupMemberInline(admin.TabularInline):
    model = GroupMember
    extra = 1


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_by', 'currency', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'currency')
    search_fields = ('name', 'description')
    inlines = [GroupMemberInline]


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'joined_at')
    list_filter = ('role',)
