from django.db import models


class CrawlerModelManager(models.Manager):
    """
    Or use db router?
    https://docs.djangoproject.com/en/3.2/topics/db/multi-db/
    """

    def get_queryset(self):
        qs = super(CrawlerModelManager, self).get_queryset()
        if self._db is not None:
            qs = qs.using(self._db)
        return qs
