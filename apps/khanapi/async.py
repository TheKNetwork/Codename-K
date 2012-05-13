from celery.task import Task
from celery.registry import tasks

class UpdateUserRelatedInfo(Task):

    def run(self, user_id, **kwargs):

        try:
            user = User.objects.get(id=user_id)
            print "Running asynchron"

        except Exception, e:
            print e

tasks.register(UpdateUserRelatedInfo)