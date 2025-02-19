from .models import Category

def menu_links(request):
    """
    Adds all categories to the template context for global use.
    """
    links = Category.objects.all()
    return dict(links=links)