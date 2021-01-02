from django.contrib import admin

from .models import Story


class TrendingListFilter(admin.SimpleListFilter):
    title = 'Trending'

    parameter_name = 'trending'

    def lookups(self, request, model_admin):
        return (
            ('true', 'is trending'),
            ('false', 'is not trending'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(trending_order__gte=1,
                                   trending_order__lte=6).order_by('trending_order')
        if self.value() == 'false':
            return queryset.filter(trending_order=None)


class MainListFilter(admin.SimpleListFilter):
    title = 'Main'

    parameter_name = 'main'

    def lookups(self, request, model_admin):
        return (
            ('true', 'is main'),
            ('false', 'is not main'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(main_order__gte=1,
                                   main_order__lte=6).order_by('trending_order')
        if self.value() == 'false':
            return queryset.filter(main_order=None)


class StoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'writer_id', 'writer', 'title', 'main_order', 'trending_order', 'published_at')
    list_display_links = ('title',)
    list_editable = ('main_order', 'trending_order')
    list_filter = (MainListFilter, TrendingListFilter)
    ordering = ('-published_at',)
    search_fields = ['writer__username', 'writer__userprofile__name']


admin.site.register(Story, StoryAdmin)
