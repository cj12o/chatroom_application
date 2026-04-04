from django.db.models import Count, Q

from base.logger import logger
from base.models.message_model import Vote
from base.models.poll_model import Poll, PollVote


def get_vote_counts(message_id: int) -> dict:
    """
    Returns {"upvotes": N, "downvotes": N} for a message
    using a single aggregate query instead of two filter+count calls.
    """
    result = Vote.objects.filter(message_id=message_id).aggregate(
        upvotes=Count('id', filter=Q(vote=1)),
        downvotes=Count('id', filter=Q(vote=-1)),
    )
    return result


def get_user_votes_for_room(user_id: int, room_id: int) -> list[dict]:
    """
    Returns all votes by a user in a room.
    Uses select_related to avoid N+1 on message access.
    """
    votes = (
        Vote.objects
        .filter(user_id=user_id, room_id=room_id)
        .select_related('message')
    )
    return [{"message_id": v.message_id, "vote_type": v.vote} for v in votes]


def get_poll_vote_summary(room_id: int, user=None) -> dict:
    """
    Returns poll vote counts + user's vote for all polls in a room.
    Replaces the N+1 loop that queried PollVote per choice per poll.

    Output: {
        poll_id: {
            0: count, 1: count, ...,
            "user_has_vote": bool,
            "user_vote": int
        }
    }
    """
    polls = Poll.objects.filter(room_id=room_id).select_related('message')

    # Prefetch all poll votes in one query
    poll_ids = [p.id for p in polls]
    all_votes = (
        PollVote.objects
        .filter(poll_id__in=poll_ids)
        .values('poll_id', 'choiceSelected')
        .annotate(cnt=Count('id'))
    )

    # Build a lookup: {poll_id: {choice: count}}
    vote_counts = {}
    for row in all_votes:
        pid = row['poll_id']
        if pid not in vote_counts:
            vote_counts[pid] = {}
        vote_counts[pid][row['choiceSelected']] = row['cnt']

    # Get user's votes in one query
    user_votes = {}
    if user and user.is_authenticated:
        for uv in PollVote.objects.filter(poll_id__in=poll_ids, user=user):
            user_votes[uv.poll_id] = uv.choiceSelected

    # Assemble result
    result = {}
    for poll in polls:
        choices = [idx for idx, _ in enumerate(poll.choices)]
        dct = {}
        counts = vote_counts.get(poll.id, {})
        for ch in choices:
            dct[ch] = counts.get(ch, 0)
        dct["user_has_vote"] = poll.id in user_votes
        dct["user_vote"] = user_votes.get(poll.id, -1)
        result[poll.id] = dct

    return result
