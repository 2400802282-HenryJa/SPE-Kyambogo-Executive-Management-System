from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class TreasuryAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Use on any view that shows confidential treasury/finance data."""

    def test_func(self):
        return self.request.user.is_treasury_authorised


class ContactAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Contacts are restricted to the President, VP, CAO and developer."""

    def test_func(self):
        return self.request.user.can_access_contacts
