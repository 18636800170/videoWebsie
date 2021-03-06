from hashlib import md5

import redis as redis
from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils.functional import cached_property
from django.views.decorators.cache import cache_page
from web.helprs.composer import get_posts_by_cid
from web.models.comment import Comment
from web.models.post import Post

r = redis.Redis()


@cached_property
def count(self):
    sql, params = self.object_list.query.sql_with_params()
    sql = sql % params
    cache_key = md5(sql.encode("utf-8")).hexdigest()
    # cache_key = "%s_count" % self.object_list.model.__name__

    row_count = cache.get(cache_key)
    if not row_count:
        row_count = self.object_list.count()
        cache.set(cache_key, row_count)
    return int(row_count)


Paginator.count = count


# 设置过期时间
# @cache_page(60 * 15)
def show_list(request):
    composer=request.composer
    post_list = Post.objects.order_by("-like_counts")
    paginator = Paginator(post_list, 40)
    posts = paginator.page(1)
    for post in posts:
        post.composers = post.get_composers()
    return render(request, "post_list.html", {"posts": posts})


def post_detail(request, pid):
    post = Post.get(pid=pid)
    post.composers = post.get_composers()
    first_composer = post.composers[0]
    first_composer.posts = get_posts_by_cid(first_composer.cid, 6)  # get the first 6 videos of the author
    return render(request, 'post.html', locals())


def get_comments(request):
    pid = request.GET.get("id")
    # print(pid)
    page = request.GET.get("page")
    comment_list = Comment.objects.filter(pid=pid).order_by("-created_at")
    paginator = Paginator(comment_list, 10)
    comments = paginator.page(page)
    return render(request, "comments.html", locals())
