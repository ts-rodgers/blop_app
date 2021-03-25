from tests.asgi.conftest import GraphQLClient


def test_watch_post(client: GraphQLClient, post, post_factory, comment_fetcher):
    with client.subscribe(
        """
        subscription watchPost($postId: Int!) {
            watchPost(id: $postId) {
                __typename
                ... on PostUpdatedEvent {
                    id
                    content
                }
                ... on CommentAddedEvent {
                    id
                    content
                }
            }
        }
        """,
        variables={"postId": post.id},
    ) as subscription:
        new_content = post_factory.build().content
        result = client.execute(
            """
            mutation updatePost($postId: Int!, $content: String!) {
                updatePost(id: $postId, content: $content) {
                    __typename
                }
            }
            """,
            variables={"postId": post.id, "content": new_content},
            access_token=post.author.access_token,
        )
        assert result.get("errors") is None
        data = next(subscription)["data"]

        assert data["watchPost"]["id"] == post.id
        assert data["watchPost"]["content"] == new_content

        comment_content = post_factory.build().content
        result = client.execute(
            """
            mutation addComment($postId: Int!, $content: String!) {
                addComment(postId: $postId, content: $content) {
                    __typename
                }
            }
            """,
            variables={"postId": post.id, "content": comment_content},
            access_token=post.author.access_token,
        )
        assert result.get("errors") is None
        data = next(subscription)["data"]

        assert data["watchPost"]["__typename"] == "CommentAddedEvent"
        assert data["watchPost"]["id"] != post.id

        assert comment_fetcher.fetch(data["watchPost"]["id"]).content == comment_content


def test_subscription_cleanup_on_unsubscribe(
    client: GraphQLClient, post, post_factory, comment_fetcher
):
    with client.subscribe(
        """
        subscription watchPost($postId: Int!) {
            watchPost(id: $postId) {
                __typename
                ... on PostUpdatedEvent {
                    id
                    content
                }
                ... on CommentAddedEvent {
                    id
                    content
                }
            }
        }
        """,
        variables={"postId": post.id},
    ) as subscription:
        # do nothing with subscription; simply unsubscribe
        subscription.unsubscribe()
        result = client.execute(
            """
            mutation updatePost($postId: Int!, $content: String!) {
                updatePost(id: $postId, content: $content) {
                    __typename
                }
            }
            """,
            variables={"postId": post.id},
            access_token=post.author.access_token,
        )