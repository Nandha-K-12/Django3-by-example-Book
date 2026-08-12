from django.urls import path
from . import views
from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import PostSitemap
from .feeds import LatestPostsFeed
from django.conf import settings
from django.conf.urls.static import static
app_name = 'blog'
sitemaps = {
    'posts': PostSitemap,
}
urlpatterns = [
   path('',views.PostListView.as_view(),name='post_list'),
   path('tag/<slug:tag_slug>/', views.PostListView.as_view(), name='post_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',views.post_detail,name='post_detail'),
    path('<int:post_id>/share/',views.post_share,name='post_share'),
    path(
    'sitemap.xml',
    sitemap,
    {'sitemaps': sitemaps},
    name='django.contrib.sitemaps.views.sitemap'
),
     path(
        'feed/',
        LatestPostsFeed(),
        name='post_feed',
    ),
    path('search/', views.post_search, name='post_search'),
    
]  
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)