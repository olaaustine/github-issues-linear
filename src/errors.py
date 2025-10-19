class GraphQLError(Exception):
    """Base class for all GraphQL related errors. Raised when a GraphQL operation fails."""

    pass


class ResponseNot200Error(Exception):
    """Raised when the HTTP response status is not 200."""

    pass
