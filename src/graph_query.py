mutation = """
mutation IssueCreate($input: IssueCreateInput!) {
  issueCreate(input: $input) {
    success
    issue { id identifier url }
  }
}
"""

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

TEAM_BY_NAME = """
query TeamIdByName($name: String!) {
  teams(filter: { name: { eqIgnoreCase: $name } }, first: 5) {
    nodes { id name key }
  }
}
"""
