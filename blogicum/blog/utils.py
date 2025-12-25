from django.db.models import Q, Count
from django.utils import timezone


def order_date(queryset):
    return queryset.order_by('-pub_date')


def annotate_pub_coms(queryset):
    return queryset.annotate(
        comment_count=Count('comments', filter=Q(comments__is_published=True))
    )


def filter_published_posts(queryset):
    return queryset.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )