import random
from typing import List, Type

import pytest
from pytest_factoryboy import LazyFixture

from blog_app.comments.types import Comment
from .conftest import (
    GraphQLClient,
    FakeUser,
    FakePost,
    FakeComment,
    Fetcher,
    PostFactory,
    CommentFactory,
)
from .helpers import get_item_repr


def test_can_get_all_post_comments_without_auth(
    client: GraphQLClient, comment_factory: Type[PostFactory], comment: FakeComment
):
    post = comment.post

    comment_factory.clear()  # delete all previous comments
    comments: List[FakeComment] = comment_factory.create_batch(100, post=post)

    result = client.execute(
        """
        query getAllCommentsForPost($postId: Int!) {
            posts {
                byId(ids: [$postId]) {
                    comments {
                        allItems {
                            id
                            content
                            author {
                                id
                                name
                            }
                            authorId
                            updated
                            created
                        }
                    }
                }
            }
        }
        """,
        variables={"postId": post.id},
    )
    assert result.get("errors") is None

    all_expected_comments = [
        get_item_repr(
            comment,
            strip_keys=["post_id", "reactions"],
            author_id="authorId",
            created=lambda dt: dt.isoformat(),
            updated=lambda dt: dt.isoformat(),
        )
        for comment in comments
    ]
    assert (
        result["data"]["posts"]["byId"][0]["comments"]["allItems"]
        == all_expected_comments
    )


def test_add_comment_requires_auth(
    client, comment_factory: Type[CommentFactory], post: FakePost
):
    comment: FakeComment = comment_factory.build()
    result = client.execute(
        """
        mutation addComment($postId: Int!, $content: String!) {
            addComment(postId: $postId, content: $content) {
                ... on AuthError {
                    reason
                }
                ... on CommentResponse {
                    id
                }
            }
        }
        """,
        variables={"postId": post.id, "content": comment.content},
    )

    assert result.get("errors") is None
    assert "id" not in result["data"]["addComment"]
    assert result["data"]["addComment"]["reason"] == "UNAUTHORIZED"


def test_add_comment_with_auth(
    client, comment_factory: Type[CommentFactory], post: FakePost
):
    comment: FakeComment = comment_factory.build()
    result = client.execute(
        """
        mutation addComment($postId: Int!, $content: String!) {
            addComment(postId: $postId, content: $content) {
                ... on AuthError {
                    reason
                }
                ... on CommentResponse {
                    id
                    content
                }
            }
        }
        """,
        variables={"postId": post.id, "content": comment.content},
        access_token=post.author.access_token,
    )

    assert result.get("errors") is None
    assert "reason" not in result["data"]["addComment"]
    assert "id" in result["data"]["addComment"]
    assert result["data"]["addComment"]["content"] == comment.content

    created_comment = comment_factory.fetch(result["data"]["addComment"]["id"])
    assert created_comment.content == comment.content


def test_update_comment_requires_auth(
    client: GraphQLClient,
    comment_factory: Type[CommentFactory],
    comment_fetcher: Fetcher[Comment],
    comment: FakeComment,
):
    """Check that updating a comment without being logged returns AuthError."""
    new_content = comment_factory.build().content
    result = client.execute(
        """
        mutation updateComment($commentId: Int!, $content: String!) {
            updateComment(id: $commentId, content: $content) {
                ... on AuthError {
                    reason
                }
                ... on CommentResponse {
                    id
                    content
                }
            }
        }
        """,
        variables={"commentId": comment.id, "content": new_content},
    )

    assert result.get("errors") is None

    assert "id" not in result["data"]["updateComment"]
    assert "content" not in result["data"]["updateComment"]
    assert result["data"]["updateComment"]["reason"] == "UNAUTHORIZED"
    assert comment_fetcher.fetch(comment.id).content != new_content  # type: ignore


@pytest.mark.parametrize(
    "comment__author",
    [
        LazyFixture(lambda user_factory: user_factory.create())
    ],  # ensure post and comment have different authors
)
def test_update_comment_requires_auth_from_creating_user(
    client: GraphQLClient,
    comment_factory: Type[CommentFactory],
    comment_fetcher: Fetcher[Comment],
    comment: FakeComment,
):
    """Check that updating a comment as another user returns AuthError."""
    new_content = comment_factory.build().content
    result = client.execute(
        """
        mutation updateComment($commentId: Int!, $content: String!) {
            updateComment(id: $commentId, content: $content) {
                ... on AuthError {
                    reason
                }
                ... on CommentResponse {
                    id
                    content
                }
            }
        }
        """,
        variables={"commentId": comment.id, "content": new_content},
        access_token=comment.post.author.access_token,
    )

    assert result.get("errors") is None

    assert "id" not in result["data"]["updateComment"]
    assert "content" not in result["data"]["updateComment"]
    assert result["data"]["updateComment"]["reason"] == "UNAUTHORIZED"
    assert comment_fetcher.fetch(comment.id).content != new_content  # type: ignore


def test_update_comment_with_auth_from_creating_user(
    client: GraphQLClient,
    comment_factory: Type[CommentFactory],
    comment_fetcher: Fetcher[Comment],
    comment: FakeComment,
):
    """Check that updating a comment as creating user works."""
    new_content = comment_factory.build().content
    result = client.execute(
        """
        mutation updateComment($commentId: Int!, $content: String!) {
            updateComment(id: $commentId, content: $content) {
                ... on AuthError {
                    reason
                }
                ... on CommentResponse {
                    id
                    content
                }
            }
        }
        """,
        variables={"commentId": comment.id, "content": new_content},
        access_token=comment.author.access_token,
    )

    assert result.get("errors") is None

    assert "reason" not in result["data"]["updateComment"]
    assert result["data"]["updateComment"]["id"] == comment.id
    assert result["data"]["updateComment"]["content"] == new_content
    assert comment_fetcher.fetch(comment.id).content == new_content  # type: ignore


def test_delete_comment_requires_auth(
    client: GraphQLClient,
    comment_fetcher: Fetcher[Comment],
    comment: FakeComment,
):
    """Check that updating a comment without being logged returns AuthError."""
    result = client.execute(
        """
        mutation deleteComment($commentId: Int!) {
            deleteComment(id: $commentId) {
                ... on AuthError {
                    reason
                }
                ... on CommentDeletionResponse {
                    id
                }
            }
        }
        """,
        variables={"commentId": comment.id},
    )

    assert result.get("errors") is None

    assert "id" not in result["data"]["deleteComment"]
    assert "content" not in result["data"]["deleteComment"]
    assert result["data"]["deleteComment"]["reason"] == "UNAUTHORIZED"
    assert comment_fetcher.fetch(comment.id) is not None


@pytest.mark.parametrize(
    "comment__author",
    [
        LazyFixture(lambda user_factory: user_factory.create())
    ],  # ensure post and comment have different authors
)
def test_delete_comment_requires_auth_from_creating_user(
    client: GraphQLClient,
    comment_fetcher: Fetcher[Comment],
    comment: FakeComment,
):
    """Check that deleting a comment as another user returns AuthError."""
    result = client.execute(
        """
        mutation deleteComment($commentId: Int!) {
            deleteComment(id: $commentId) {
                ... on AuthError {
                    reason
                }
                ... on CommentDeletionResponse {
                    id
                }
            }
        }
        """,
        variables={"commentId": comment.id},
        access_token=comment.post.author.access_token,
    )

    assert result.get("errors") is None

    assert "id" not in result["data"]["deleteComment"]
    assert "content" not in result["data"]["deleteComment"]
    assert result["data"]["deleteComment"]["reason"] == "UNAUTHORIZED"
    assert comment_fetcher.fetch(comment.id) is not None


def test_delete_comment_with_auth_from_creating_user(
    client: GraphQLClient,
    comment_fetcher: Fetcher[Comment],
    comment: FakeComment,
):
    """Check that updating a comment as creating user works."""
    result = client.execute(
        """
        mutation deleteComment($commentId: Int!) {
            deleteComment(id: $commentId) {
                ... on AuthError {
                    reason
                }
                ... on CommentDeletionResponse {
                    id
                }
            }
        }
        """,
        variables={"commentId": comment.id},
        access_token=comment.author.access_token,
    )

    assert result.get("errors") is None

    assert "reason" not in result["data"]["deleteComment"]
    assert result["data"]["deleteComment"]["id"] == comment.id
    assert comment_fetcher.fetch(comment.id) is None


def test_delete_non_existent_comment_returns_error(
    client: GraphQLClient,
    comment: FakeComment,
):
    """Check that updating a comment as creating user works."""
    result = client.execute(
        """
        mutation deleteComment($commentId: Int!) {
            deleteComment(id: $commentId) {
                __typename
                ... on AuthError {
                    reason
                }
                ... on CommentDeletionResponse {
                    id
                }
            }
        }
        """,
        variables={"commentId": 44647746},
        access_token=comment.author.access_token,
    )

    assert result.get("errors") is None

    assert "id" not in result["data"]["deleteComment"]
    assert result["data"]["deleteComment"]["__typename"] == "ItemNotFoundError"
