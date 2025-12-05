from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Tour,Review,ContactMessage,TourImage


# ✅ Step 1: Define a resource class
class TourResource(resources.ModelResource):
    class Meta:
        model = Tour
        # optional: specify fields to import/export
        fields = ('id', 'title', 'location', 'price', 'duration', 'description', 'image_url', 'created_at')
        import_id_fields = ('title',)  # avoid duplicates based on title


class TourImageInline(admin.TabularInline):   # or admin.StackedInline
    model = TourImage
    extra = 1


# ✅ Step 2: Register in admin with import/export enabled
@admin.register(Tour)
class TourAdmin(ImportExportModelAdmin):
    resource_class = TourResource
    list_display = ('title', 'location', 'price', 'duration', 'created_at')
    search_fields = ('title', 'location')
    list_filter = ('location',)
    inlines = [TourImageInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('tour', 'user', 'rating', 'comment', 'created_at')
    search_fields = ('tour__title', 'user__username')
    list_filter = ('rating',)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message','created_at')
    search_fields = ('name', 'email', 'message')
    list_filter = ('created_at',)

admin.site.register(TourImage)