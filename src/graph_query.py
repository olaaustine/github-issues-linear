# GraphQL mutation to create a new ticket/issue
mutation = """
mutation IssueCreate($input: IssueCreateInput!) {
  issueCreate(input: $input) {
    success
    issue { id identifier url }
  }
}
"""
# Query to check if an issue with a specific title exists in a team
QUERY_WITH_TEAM = """
query IssuesByTitle($title: String!, $teamId: ID!) {
  issues(
    filter: {
      title: { eqIgnoreCase: $title }
      archivedAt: { null: true }
      team: { id: { eq: $teamId } }
    }
    first: 1
  ) {
    nodes { id identifier title url }
  }
} """

# Query to get team ID by team name
TEAM_BY_NAME = """
query TeamIdByName($name: String!) {
  teams(filter: { name: { eqIgnoreCase: $name } }, first: 5) {
    nodes { id name key }
  }
}
"""
# Query to get the status of a ticket/issue by its ID
GET_TICKETS_STATUS = """query GetIssueStatus($id: String!) {
  issue(id: $id) {
    id
    identifier
    title
    url
    state {
      id
      name
    }
  }
}
"""
