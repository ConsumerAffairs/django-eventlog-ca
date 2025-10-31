"""
Tests for eventlog models.
"""

import pytest
from django.contrib.auth.models import User
from django.test import TestCase

from eventlog.models import Log, log


@pytest.mark.django_db
class TestLogModel(TestCase):
    """Test Log model functionality."""

    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_log_creation_with_user(self):
        """Test creating a log entry with a user."""
        log_entry = Log.objects.create(
            user=self.user, action="test_action", extra={"key": "value"}
        )

        assert log_entry.user == self.user
        assert log_entry.action == "test_action"
        assert log_entry.extra == {"key": "value"}
        assert log_entry.timestamp is not None

    def test_log_creation_without_user(self):
        """Test creating a log entry without a user."""
        log_entry = Log.objects.create(user=None, action="anonymous_action", extra={})

        assert log_entry.user is None
        assert log_entry.action == "anonymous_action"

    def test_log_ordering(self):
        """Test that logs are ordered by timestamp descending."""
        log1 = Log.objects.create(user=self.user, action="first_action", extra={})
        log2 = Log.objects.create(user=self.user, action="second_action", extra={})

        logs = list(Log.objects.all())
        assert logs[0] == log2  # Most recent first
        assert logs[1] == log1

    def test_log_action_index(self):
        """Test that action field has db_index=True."""
        # This test verifies the model definition
        action_field = Log._meta.get_field("action")
        assert action_field.db_index is True

    def test_log_indexes(self):
        """Test that composite index on action and timestamp exists."""
        # Verify indexes are defined in Meta
        indexes = Log._meta.indexes
        assert len(indexes) == 1
        assert "action" in indexes[0].fields
        assert "timestamp" in indexes[0].fields


@pytest.mark.django_db
class TestLogFunction(TestCase):
    """Test log() helper function."""

    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_log_function_with_user(self):
        """Test log function creates entry with user."""
        result = log(self.user, "test_action", {"data": "test"})

        assert isinstance(result, Log)
        assert result.user == self.user
        assert result.action == "test_action"
        assert result.extra == {"data": "test"}

    def test_log_function_without_extra(self):
        """Test log function with no extra data."""
        result = log(self.user, "simple_action")

        assert result.extra == {}

    def test_log_function_with_unauthenticated_user(self):
        """Test log function handles unauthenticated user."""

        # Create a mock unauthenticated user
        class UnauthenticatedUser:
            is_authenticated = False

        unauth_user = UnauthenticatedUser()
        result = log(unauth_user, "test_action")

        assert result.user is None

    def test_log_function_with_none_user(self):
        """Test log function with None user."""
        result = log(None, "anonymous_action", {"info": "data"})

        assert result.user is None
        assert result.action == "anonymous_action"
        assert result.extra == {"info": "data"}

    def test_log_function_creates_database_entry(self):
        """Test that log function actually saves to database."""
        initial_count = Log.objects.count()
        log(self.user, "test_action")

        assert Log.objects.count() == initial_count + 1

    def test_multiple_logs_for_same_action(self):
        """Test creating multiple logs with same action."""
        log(self.user, "repeated_action", {"attempt": 1})
        log(self.user, "repeated_action", {"attempt": 2})

        logs = Log.objects.filter(action="repeated_action").order_by("-timestamp")
        assert logs.count() == 2
        assert logs[0].extra["attempt"] == 2
        assert logs[1].extra["attempt"] == 1
