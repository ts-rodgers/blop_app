import random
from typing import List, Type

import pytest

from blog_app.posts.types import Post
from .conftest import GraphQLClient, FakeUser, FakePost, Fetcher, PostFactory
from .helpers import get_item_repr


def test_can_get_all_posts_without_auth(
    client: GraphQLClient, post_factory: Type[PostFactory]
):
    posts: List[FakePost] = post_factory.create_batch(6)

    result = client.execute(
        """
        {
            posts {
                allItems {
                    id
                    title
                    authorId
                    content
                    author {
                        id
                        name
                    }
                    created
                    updated
                }
            }
        }
        """
    )
    assert result.get("errors") is None

    all_expected_posts = [
        get_item_repr(
            post,
            strip_keys=["comments"],
            author_id="authorId",
            created=lambda dt: dt.isoformat(),
            updated=lambda dt: dt.isoformat(),
        )
        for post in posts
    ]
    assert result["data"]["posts"]["allItems"] == all_expected_posts


def test_can_get_posts_by_id_without_auth(
    client: GraphQLClient, post_factory: Type[PostFactory]
):
    posts: List[FakePost] = post_factory.create_batch(6)
    random.shuffle(posts)

    result = client.execute(
        """
        query getPostsById($ids: [Int!]!) {
            posts {
                byId (ids: $ids) {
                    id
                    title
                    authorId
                    content
                    author {
                        id
                        name
                    }
                    created
                    updated
                }
            }
        }
        """,
        variables={"ids": [post.id for post in posts]},
    )
    assert result.get("errors") is None

    all_expected_posts = [
        get_item_repr(
            post,
            strip_keys=["comments"],
            author_id="authorId",
            created=lambda dt: dt.isoformat(),
            updated=lambda dt: dt.isoformat(),
        )
        for post in posts
    ]
    assert result["data"]["posts"]["byId"] == all_expected_posts


def test_create_post_bad_title(client, post_factory: Type[PostFactory]):
    post: FakePost = post_factory.build()
    result = client.execute(
        """
        mutation createPost($title: PostTitle!, $content: String!) {
            createPost(title: $title, content: $content) {
                ... on AuthError {
                    reason
                }
                ... on PostCreationResponse {
                    id
                    title
                }
            }
        }
        """,
        variables={"title": "        ", "content": post.content},
    )

    assert result.get("data") is None
    assert "cannot contain only whitespace" in result["errors"][0]["message"]


def test_create_post_requires_auth(client, post_factory: Type[PostFactory]):
    post: FakePost = post_factory.build()
    result = client.execute(
        """
        mutation createPost($title: PostTitle!, $content: String!) {
            createPost(title: $title, content: $content) {
                ... on AuthError {
                    reason
                }
            }
        }
        """,
        variables={"title": post.title, "content": post.content},
    )

    assert result.get("errors") is None
    assert result["data"]["createPost"]["reason"] == "UNAUTHORIZED"


def test_create_post_with_auth(client, user: FakeUser, post_factory: Type[PostFactory]):
    post: FakePost = post_factory.build()
    result = client.execute(
        """
        mutation createPost($title: PostTitle!, $content: String!) {
            createPost(title: $title, content: $content) {
                ... on AuthError {
                    reason
                }
                ... on PostCreationResponse {
                    id
                    title
                }
            }
        }
        """,
        variables={"title": post.title, "content": post.content},
        access_token=user.access_token,
    )

    assert result.get("errors") is None
    assert "reason" not in result["data"]["createPost"]
    assert "id" in result["data"]["createPost"]
    assert result["data"]["createPost"]["title"] == post.title

    created_post = post_factory.fetch(result["data"]["createPost"]["id"])
    assert created_post.title == post.title
    assert created_post.content == post.content


@pytest.mark.parametrize(
    "title, expected",
    [
        ("A regular title", "A regular title"),
        ("    A regular title", "A regular title"),
        ("A regular title    \n", "A regular title"),
        ("    A regular\ttitle    ", "A regular title"),
    ],
)
def test_create_post_title_coersion(
    client: GraphQLClient,
    title: str,
    expected: str,
    user: FakeUser,
    post_factory: Type[PostFactory],
):
    """Check that titles will have whitespace collapsed."""
    post: FakePost = post_factory.build()
    result = client.execute(
        """
        mutation createPost($title: PostTitle!, $content: String!) {
            createPost(title: $title, content: $content) {
                ... on AuthError {
                    reason
                }
                ... on PostCreationResponse {
                    id
                    title
                }
            }
        }
        """,
        variables={"title": title, "content": post.content},
        access_token=user.access_token,
    )

    assert result.get("errors") is None
    assert result["data"]["createPost"]["title"] == expected


@pytest.mark.parametrize(
    "variables",
    [
        {"title": "some fake title", "content": "Some fake content, etc etc"},
        {"title": "some fake title"},
        {"content": "Some fake content, etc etc"},
    ],
)
def test_update_post_requires_auth(client: GraphQLClient, variables, post: FakePost):
    """Check that updating a post without being logged returns AuthError."""
    variables["postId"] = post.id
    result = client.execute(
        """
        mutation updatePost($postId: Int!, $title: PostTitle, $content: String) {
            updatePost(id: $postId, title: $title, content: $content) {
                ... on AuthError {
                    reason
                }
                ... on PostUpdateResponse {
                    id
                    title
                }
            }
        }
        """,
        variables=variables,
    )

    assert result.get("errors") is None
    assert "id" not in result["data"]["updatePost"]
    assert "title" not in result["data"]["updatePost"]
    assert result["data"]["updatePost"]["reason"] == "UNAUTHORIZED"


@pytest.mark.parametrize(
    "variables",
    [
        {"title": "some fake title", "content": "Some fake content, etc etc"},
        {"title": "some fake title"},
        {"content": "Some fake content, etc etc"},
    ],
)
def test_update_post_requires_auth_from_creating_user(
    client: GraphQLClient, variables, user_factory, post: FakePost
):
    """Check that updating a post logged in as wrong user returns AuthError."""
    user = user_factory.create()
    variables["postId"] = post.id
    result = client.execute(
        """
        mutation updatePost($postId: Int!, $title: PostTitle, $content: String) {
            updatePost(id: $postId, title: $title, content: $content) {
                ... on AuthError {
                    reason
                }
                ... on PostUpdateResponse {
                    id
                    title
                }
            }
        }
        """,
        variables=variables,
        access_token=user.access_token,
    )

    assert result.get("errors") is None
    assert "id" not in result["data"]["updatePost"]
    assert "title" not in result["data"]["updatePost"]
    assert result["data"]["updatePost"]["reason"] == "UNAUTHORIZED"


@pytest.mark.parametrize(
    "variables",
    [
        {"title": "some fake title", "content": "Some fake content, etc etc"},
        {"title": "some fake title"},
        {"content": "Some fake content, etc etc"},
    ],
)
def test_update_post_with_auth_from_creating_user(
    client: GraphQLClient, variables, post: FakePost, post_fetcher: Fetcher[Post]
):
    """Check that updating a post logged in as creating user updates post record."""
    variables["postId"] = post.id
    result = client.execute(
        """
        mutation updatePost($postId: Int!, $title: PostTitle, $content: String) {
            updatePost(id: $postId, title: $title, content: $content) {
                ... on AuthError {
                    reason
                }
                ... on PostUpdateResponse {
                    id
                    title
                    content
                }
            }
        }
        """,
        variables=variables,
        access_token=post.author.access_token,
    )

    assert result.get("errors") is None
    assert "id" in result["data"]["updatePost"]

    updated_post = post_fetcher.fetch(result["data"]["updatePost"]["id"])

    assert updated_post is not None

    if "title" in variables:
        assert updated_post.title == result["data"]["updatePost"]["title"]
        assert variables["title"] == updated_post.title

    if "content" in variables:
        assert updated_post.content == result["data"]["updatePost"]["content"]
        assert variables["content"] == updated_post.content


def test_delete_post_as_creating_user(
    client: GraphQLClient,
    post: FakePost,
    post_fetcher: Fetcher[Post],
):
    """Check that the user who created a post can also delete it."""
    variables = {"postId": post.id}
    result = client.execute(
        """
        mutation deletePost($postId: Int!) {
            deletePost(id: $postId) {
                ... on AppError {
                    error: message
                }
                ... on PostDeletionResponse {
                    id
                }
            }
        }
        """,
        variables=variables,
        access_token=post.author.access_token,
    )

    assert result.get("errors") is None
    assert result["data"]["deletePost"].get("error") is None
    assert result["data"]["deletePost"]["id"] == post.id

    post_with_same_id = post_fetcher.fetch(post.id)
    assert post_with_same_id is None


def test_delete_post_requires_auth(
    client: GraphQLClient,
    post: FakePost,
    post_fetcher: Fetcher[Post],
):
    """Check that the user who created a post can also delete it."""
    variables = {"postId": post.id}
    result = client.execute(
        """
        mutation deletePost($postId: Int!) {
            deletePost(id: $postId) {
                ... on AuthError {
                    reason
                }
                ... on PostDeletionResponse {
                    id
                }
            }
        }
        """,
        variables=variables,
    )

    assert result.get("errors") is None
    assert result["data"]["deletePost"].get("id") is None
    assert result["data"]["deletePost"]["reason"] == "UNAUTHORIZED"

    post_with_same_id = post_fetcher.fetch(post.id)
    assert post_with_same_id is not None
