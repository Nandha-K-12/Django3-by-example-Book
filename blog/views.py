from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from taggit.models import Tag
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
)
from django.core.paginator import (
    Paginator,
    EmptyPage,
    PageNotAnInteger
)

from django.views.generic import ListView

from .models import Post
from .forms import EmailPostForm, CommentForm

class PostListView(ListView):
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

    def get_queryset(self):
        queryset = Post.published.all()
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            self.tag = get_object_or_404(Tag, slug=tag_slug)
            queryset = queryset.filter(tags__in=[self.tag])
        else:
            self.tag = None
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        slug=post,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day
    )

    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'new_comment': new_comment,
            'comment_form': comment_form,
        }
    )


def post_share(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status='published'
    )

    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data

            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )

            subject = f"{cd['name']} recommends you read {post.title}"

            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}\n\n"
                f"Sender email: {cd['email']}"
            )

            send_mail(subject,message,settings.DEFAULT_FROM_EMAIL,[cd['to']])

            sent = True

    else:
        form = EmailPostForm()

    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent
        }
    )
def post_search(request):
    query = None
    results = []

    if 'query' in request.GET:
        query = request.GET['query']

        search_vector = (
            SearchVector('title', weight='A') +
            SearchVector('body', weight='B')
        )

        search_query = SearchQuery(query)

        results = (
            Post.published
            .annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            )
            .filter(search=search_query)
            .order_by('-rank')
        )

    return render(
        request,
        'blog/post/search.html',
        {
            'query': query,
            'results': results,
        }
    )