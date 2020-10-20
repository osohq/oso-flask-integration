### Expense rules

# graphql
graphql_authorize(_: Expense);
allow(u, "query", expense) if allow(u, "read", expense);

# Pretty jank... field authz
graphql_authorize_schema(schema::Expense);
allow_field(user, "query", schema::Expense, _, "description");
allow_field(user, "query", schema::Expense, expense, "amount") if submitted(user, expense);

# rules allow_field(user, "query", schema::Expense, expense) {
#     "description",
#     "amount" if submitted(user, expense),
#     _ if user.isAdmin,
# };
# 
# rules allow(user: User) {
#     ("get", _: Expense);
#     ("get", _: Organization);
# }

# by model
allow(user: User, "read", expense: Expense) if
    submitted(user, expense);

submitted(user: User, expense: Expense) if
    user.id = expense.user_id;

### Organization rules
allow(user: User, "read", organization: Organization) if
    user.organization_id = organization.id;
