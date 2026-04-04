import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.db.models import Q

from base.models import Room, Message, ChatFileLog, MessageSummerizedStatus
from base.models.topic_model import Topic
from base.tasks.summerization_tasks import add_summerize_task
from base.services.message_services import get_lastest_moderated_unsummerized_message


class SummarizationTestBase(TestCase):
    """Shared setup for summarization tests."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass1234")
        self.topic = Topic.objects.create(topic="General")
        self.room = Room.objects.create(
            author=self.user,
            name="Test Room",
            description="A room for testing",
            parent_topic=self.topic,
            topic="testing",
        )
        
        # ChatFileLog is auto-created by the post_save signal on Room
        self.chat_log = ChatFileLog.objects.get(room=self.room)

    def _create_message(self, text, is_moderated=True, is_unsafe=False):
        """Helper to create a message with given moderation state."""
        return Message.objects.create(
            room=self.room,
            author=self.user,
            message=text,
            is_moderated=is_moderated,
            is_unsafe=is_unsafe,
        )


class TestMessageSummerizedStatusSignal(SummarizationTestBase):
    """Test that creating a Message auto-creates a MessageSummerizedStatus."""

    def test_status_created_on_message_save(self):
        msg = self._create_message("hello world")
        self.assertTrue(
            MessageSummerizedStatus.objects.filter(message=msg).exists()
        )

    def test_status_defaults_to_false(self):
        msg = self._create_message("hello world")
        status = MessageSummerizedStatus.objects.get(message=msg)
        self.assertFalse(status.status)

    def test_no_duplicate_status_on_message_update(self):
        msg = self._create_message("hello")
        msg.message = "hello updated"
        msg.save()
        self.assertEqual(
            MessageSummerizedStatus.objects.filter(message=msg).count(), 1
        )


class TestChatFileLog(SummarizationTestBase):
    """Test ChatFileLog model methods."""

    def test_chat_file_log_created_with_room(self):
        self.assertTrue(ChatFileLog.objects.filter(room=self.room).exists())

    def test_get_summary_empty_by_default(self):
        self.assertEqual(ChatFileLog.get_summary(self.room.id), "")

    def test_append_summary(self):
        ChatFileLog.append_summary(self.room.id, "First summary.")
        self.assertEqual(ChatFileLog.get_summary(self.room.id), "First summary.")

    def test_append_summary_concatenates(self):
        ChatFileLog.append_summary(self.room.id, "Part one.")
        ChatFileLog.append_summary(self.room.id, "Part two.")
        summary = ChatFileLog.get_summary(self.room.id)
        self.assertIn("Part one.", summary)
        self.assertIn("Part two.", summary)

    def test_get_summary_nonexistent_room(self):
        self.assertEqual(ChatFileLog.get_summary(99999), "")


class TestGetLatestModeratedUnsummerizedMessage(SummarizationTestBase):
    """Test the service function that fetches unsummarized messages."""

    def test_returns_moderated_safe_unsummarized(self):
        self._create_message("safe msg", is_moderated=True, is_unsafe=False)
        result = get_lastest_moderated_unsummerized_message(self.room.id, 10)
        self.assertEqual(result, ["safe msg"])

    def test_excludes_unmoderated(self):
        self._create_message("unmod msg", is_moderated=False, is_unsafe=False)
        result = get_lastest_moderated_unsummerized_message(self.room.id, 10)
        self.assertEqual(result, [])

    def test_excludes_unsafe(self):
        self._create_message("toxic msg", is_moderated=True, is_unsafe=True)
        result = get_lastest_moderated_unsummerized_message(self.room.id, 10)
        self.assertEqual(result, [])

    def test_excludes_already_summarized(self):
        msg = self._create_message("old msg", is_moderated=True, is_unsafe=False)
        MessageSummerizedStatus.objects.filter(message=msg).update(status=True)
        result = get_lastest_moderated_unsummerized_message(self.room.id, 10)
        self.assertEqual(result, [])

    def test_respects_k_limit(self):
        for i in range(5):
            self._create_message(f"msg {i}", is_moderated=True, is_unsafe=False)
        result = get_lastest_moderated_unsummerized_message(self.room.id, 3)
        self.assertEqual(len(result), 3)

    def test_returns_empty_for_k_zero(self):
        self._create_message("msg", is_moderated=True, is_unsafe=False)
        result = get_lastest_moderated_unsummerized_message(self.room.id, 0)
        self.assertEqual(result, [])


@override_settings(SUMMERIZATION_BATCH_SIZE=10, LLM_MODEL_SUMMERIZATION="gpt-3.5-turbo")
class TestAddSummerizeTask(SummarizationTestBase):
    """Test the Celery summarization task with mocked LLM."""

    @patch("base.tasks.summerization_tasks.get_model")
    @patch("base.tasks.summerization_tasks.get_prompt", return_value="Summarize these messages.")
    def test_task_calls_llm_and_saves_summary(self, mock_prompt, mock_get_model):
        # Create enough moderated messages
        for i in range(10):
            self._create_message(f"Message number {i}", is_moderated=True, is_unsafe=False)

        # Mock the LLM response
        mock_model = MagicMock()
        mock_model.invoke.return_value = MagicMock(content="This is a test summary.")
        mock_get_model.return_value = mock_model

        # Run the task synchronously
        add_summerize_task({"room_id": self.room.id})

        # LLM was called
        mock_model.invoke.assert_called_once()

        # Summary was appended to ChatFileLog
        summary = ChatFileLog.get_summary(self.room.id)
        self.assertIn("This is a test summary.", summary)

        # All MessageSummerizedStatus entries are now True
        unsummarized = MessageSummerizedStatus.objects.filter(
            Q(message__room=self.room) & Q(status=False)
        ).count()
        self.assertEqual(unsummarized, 0)

    @patch("base.tasks.summerization_tasks.get_model")
    @patch("base.tasks.summerization_tasks.get_prompt", return_value="Summarize.")
    def test_task_skips_when_no_messages(self, mock_prompt, mock_get_model):
        # No messages exist — task should return early
        add_summerize_task({"room_id": self.room.id})
        mock_get_model.assert_not_called()

    @patch("base.tasks.summerization_tasks.get_model", return_value=None)
    @patch("base.tasks.summerization_tasks.get_prompt", return_value="Summarize.")
    def test_task_handles_model_not_found(self, mock_prompt, mock_get_model):
        for i in range(10):
            self._create_message(f"msg {i}", is_moderated=True, is_unsafe=False)

        # Should not raise — error is caught internally
        add_summerize_task({"room_id": self.room.id})

        # Summary should remain empty since model was None
        self.assertEqual(ChatFileLog.get_summary(self.room.id), "")

    @patch("base.tasks.summerization_tasks.get_model")
    @patch("base.tasks.summerization_tasks.get_prompt", return_value="Summarize.")
    def test_task_passes_message_texts_to_llm(self, mock_prompt, mock_get_model):
        messages = ["Hello everyone", "How are you?", "Great discussion"]
        for text in messages:
            self._create_message(text, is_moderated=True, is_unsafe=False)

        mock_model = MagicMock()
        mock_model.invoke.return_value = MagicMock(content="Summary")
        mock_get_model.return_value = mock_model

        add_summerize_task({"room_id": self.room.id})

        # Verify the human message contains the actual message texts
        call_args = mock_model.invoke.call_args[0][0]
        human_msg_content = call_args[1].content  # Second arg is HumanMessage
        for text in messages:
            self.assertIn(text, human_msg_content)
