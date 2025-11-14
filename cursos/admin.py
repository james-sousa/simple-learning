

from django.contrib import admin

from .models import (
    Course, Enrollment, Announcement, Comment, Lesson, Material,
    LessonProgress, CourseProgress, Certificate
)


class CourseAdmin(admin.ModelAdmin):

    list_display = ['name', 'slug', 'start_date', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

class MaterialInlineAdmin(admin.StackedInline):
    model = Material

class LessonAdmin(admin.ModelAdmin):

    list_display = ['name', 'number', 'course', 'release_date']
    search_fields = ['name', 'description']
    list_filter = ['created_at']

    inlines = [
        MaterialInlineAdmin
    ]

class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'completed', 'completed_at']
    search_fields = ['user__username', 'lesson__name']
    list_filter = ['completed', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'progress_percentage', 'completed_lessons', 'total_lessons', 'completed_at']
    search_fields = ['user__username', 'course__name']
    list_filter = ['completed_at', 'created_at']
    readonly_fields = ['progress_percentage', 'completed_lessons', 'total_lessons', 'created_at', 'updated_at']

class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_number', 'user', 'course', 'issued_at']
    search_fields = ['user__username', 'course__name', 'certificate_number']
    list_filter = ['issued_at']
    readonly_fields = ['certificate_number', 'issued_at']

admin.site.register(Course, CourseAdmin)
admin.site.register([Enrollment, Announcement, Comment, Material])
admin.site.register(Lesson, LessonAdmin)
admin.site.register(LessonProgress, LessonProgressAdmin)
admin.site.register(CourseProgress, CourseProgressAdmin)
admin.site.register(Certificate, CertificateAdmin)

