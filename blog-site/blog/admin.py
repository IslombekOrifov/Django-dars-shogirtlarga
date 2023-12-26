from django.contrib import admin

from blog.models import (
    Post, Blog, Author, Entry
)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'status', 'publish', 'created', 'updated')
    list_filter = ['status', 'created', 'publish', 'author']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']
    

admin.site.register(Blog)
admin.site.register(Author)
admin.site.register(Entry)