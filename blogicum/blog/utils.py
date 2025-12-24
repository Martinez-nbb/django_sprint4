from django.db.models import Count, Q


def annotate_published_comments(queryset):
    return queryset.annotate(
        comment_count=Count('comments', filter=Q(comments__is_published=True))
    )

def ordering_by_pub_date(queryset):
    return queryset.order_by('-pub_date')

