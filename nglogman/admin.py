from django.contrib import admin
from .models import LGNode, Task, NodeGroup
from nglm_grpc.gRPCMethods import scheduleTask, SCHEDULER


# Register your models here.
@admin.register(LGNode)
class ReadOnlyAdmin(admin.ModelAdmin):
    readonly_fields = []
    change_form_template = "admin/admin_readonly.html"

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + \
               [field.name for field in obj._meta.fields] + \
               [field.name for field in obj._meta.many_to_many]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        scheduleTask(obj)
        print('scheduleTask called')
        super().save_model(request, obj, form, change)
        if 'Scheduled' not in obj.status:
            obj.status = 'Scheduled'
            obj.save()

    def delete_model(self, request, obj):
        import apscheduler.jobstores.base as base
        try:
            SCHEDULER.remove_job(str(obj.taskUUID))
        except base.JobLookupError:
            pass
        if obj.assignedNode.currentTask == obj.taskUUID:
            obj.assignedNode.nodes.all().update(
                status='Available', currentTask=None
            )
            obj.assignedNode.currentTask = None
            obj.assignedNode.save()
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            import apscheduler.jobstores.base as base
            try:
                SCHEDULER.remove_job(str(obj.taskUUID))
            except base.JobLookupError:
                pass

            if obj.assignedNode.currentTask == obj.taskUUID:
                obj.assignedNode.nodes.all().update(
                    status='Available', currentTask=None
                )
                obj.assignedNode.currentTask = None
                obj.assignedNode.save()
            obj.delete()


admin.site.site_title = 'NGLogman Administration'
admin.site.site_header = 'NGLogman Administration'
admin.site.index_title = 'Admin Dashboard'
admin.site.register(NodeGroup)
