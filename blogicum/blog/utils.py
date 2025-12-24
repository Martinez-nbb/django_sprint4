from django.db.models import Count, Q

def order_date(queryset):
    return queryset.order_by('-pub_date')

def annotate_pub_coms(queryset):
    return queryset.annotate(
        comment_count=Count('comments', filter=Q(comments__is_published=True))
    )
