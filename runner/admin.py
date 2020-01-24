from django.contrib import admin
from .models import Pipeline, Run, Port, ExecutionEvents


class PipelineAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'github', 'version', 'output_directory')


class RunAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'app', 'tags', 'status', 'execution_id', 'created_date')
    ordering = ('-created_date',)


class PortAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'run', 'db_value')
    raw_id_fields = ("run",)
    ordering = ('run',)
    search_fields = ('run__id',)


admin.site.register(Run, RunAdmin)
admin.site.register(Port, PortAdmin)
admin.site.register(Pipeline, PipelineAdmin)
admin.site.register(ExecutionEvents)
