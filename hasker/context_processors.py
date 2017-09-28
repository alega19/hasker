from .models import Question


def trending(req):
    return {
        'trending': Question.objects.order_by('-rating', '-creation_date')[:20]
    }
