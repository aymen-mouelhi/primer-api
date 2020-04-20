class Transaction(object):
    """
    A transaction object.
    """

    def __init__(self, id, amount, merchant_account_id, plan_id, recurring, refund, status, transaction_source,
                 created_at):
        """
        Creates a transaction Object based on the provided attributes.
        """
        self.id = id
        self.amount = amount
        self.merchant_account_id = merchant_account_id
        self.plan_id = plan_id
        self.recurring = recurring
        self.refund = refund
        self.status = status
        self.transaction_source = transaction_source
        self.created_at = created_at

    def __repr__(self):
        """
        Returns a typical repr with a simple representation of the transaction id and amount.
        """
        return u'<Transaction id={i}, amount={a}>'.format(
            i=self.id,
            a=self.amount
        )

    @property
    def is_validated(self):
        """
        Returns whether or not the transaction is validated.
        """
        return self.status == "processed"
