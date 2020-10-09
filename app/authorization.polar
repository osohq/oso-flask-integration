### Expense rules

# graphql
graphql_authorize(_: Expense);
allow(u, "query", expense) if allow(u, "read", expense);

# by model
allow(user: User, "read", expense: Expense) if
    submitted(user, expense);

submitted(user: User, expense: Expense) if
    user.id = expense.user_id;

### Organization rules
allow(user: User, "read", organization: Organization) if
    user.organization_id = organization.id;
