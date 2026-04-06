from django.core.management.base import BaseCommand
from base.models import Topic, Room, Message,UserProfile
from base.models.Room_Moderation_model import RoomModerationType
from django.contrib.auth.models import User
from base.services.chroma_services import add_room

ROOMS = [
    {"name": "Tech Talk",         "description": "Discuss the latest in technology and software.",      "topic": "Technology",     "tags": {"tags": ["python", "AI", "web"]}},
    {"name": "AI Frontier",       "description": "Explore artificial intelligence breakthroughs.",       "topic": "Technology",     "tags": {"tags": ["AI", "ML", "deep learning"]}},
    {"name": "Healthy Living",    "description": "Tips and discussions on health and wellness.",         "topic": "Health",         "tags": {"tags": ["fitness", "diet", "mental health"]}},
    {"name": "Startup Hub",       "description": "Entrepreneurs sharing ideas and experiences.",         "topic": "Business",       "tags": {"tags": ["startup", "VC", "growth"]}},
    {"name": "Wanderlust",        "description": "Share travel stories and destination tips.",           "topic": "Travel",         "tags": {"tags": ["travel", "adventure", "culture"]}},
    {"name": "Cinema Club",       "description": "Movie reviews, recommendations, and discussions.",     "topic": "Entertainment",  "tags": {"tags": ["movies", "reviews", "streaming"]}},
    {"name": "Learn Together",    "description": "Collaborative learning across all subjects.",          "topic": "Education",      "tags": {"tags": ["study", "courses", "books"]}},
    {"name": "Finance & Wealth",  "description": "Personal finance, investing, and wealth building.",   "topic": "Business",       "tags": {"tags": ["investing", "stocks", "crypto"]}},
    {"name": "Music Lounge",      "description": "Everything music — artists, albums, genres.",         "topic": "Entertainment",  "tags": {"tags": ["music", "concerts", "playlists"]}},
    {"name": "Daily Wellness",    "description": "Mindfulness, meditation, and daily health habits.",   "topic": "Lifestyle",      "tags": {"tags": ["mindfulness", "wellness", "habits"]}},
]

MESSAGES = [
    # Tech Talk
    ("Tech Talk", "alice",  "Has anyone tried the new Python 3.13 features?"),
    ("Tech Talk", "bob",    "Yes! The free-threaded mode is a game changer for concurrency."),
    ("Tech Talk", "charlie","I've been experimenting with it — the JIT improvements are noticeable."),
    # AI Frontier
    ("AI Frontier", "bob",    "GPT-5 benchmarks look impressive, but open-source models are catching up fast."),
    ("AI Frontier", "alice",  "Agreed — Llama 4 is surprisingly competitive on reasoning tasks."),
    ("AI Frontier", "charlie","The gap is narrowing every quarter. Exciting times!"),
    ("AI Frontier", "alice",  "Anyone benchmarked it on RAG pipelines specifically?"),
    # Healthy Living
    ("Healthy Living", "charlie","30-minute morning walks have completely changed my energy levels."),
    ("Healthy Living", "alice",  "Same! Combining it with intermittent fasting made a huge difference."),
    # Startup Hub
    ("Startup Hub", "bob",    "What's the best way to validate an MVP before spending on dev?"),
    ("Startup Hub", "alice",  "Landing page + waitlist. Measure sign-ups before writing a single line of code."),
    ("Startup Hub", "charlie","I'd add: talk to 10 potential customers first. Nothing beats qualitative feedback."),
    # Wanderlust
    ("Wanderlust", "alice",  "Japan in cherry blossom season is absolutely breathtaking."),
    ("Wanderlust", "charlie","Fully agree — Kyoto in early April is on my bucket list!"),
    ("Wanderlust", "bob",    "Any budget tips for travelling through Southeast Asia?"),
    # Cinema Club
    ("Cinema Club", "charlie","Just watched Dune Part Two — the cinematography is stunning."),
    ("Cinema Club", "bob",    "Denis Villeneuve never misses. The score is incredible too."),
    # Learn Together
    ("Learn Together", "alice",  "Anki has been transformative for my spaced-repetition studying."),
    ("Learn Together", "bob",    "Pair it with active recall and you'll retain 10× more."),
    ("Learn Together", "charlie","I use it for language learning — highly recommend for vocabulary."),
    ("Learn Together", "alice",  "Any good decks for data structures and algorithms?"),
    # Finance & Wealth
    ("Finance & Wealth", "bob",    "Index funds over stock picking — the data is pretty clear at this point."),
    ("Finance & Wealth", "charlie","Agreed. Low-cost ETFs and dollar-cost averaging beats most active funds."),
    # Music Lounge
    ("Music Lounge", "alice",  "Kendrick's last album was a masterpiece from start to finish."),
    ("Music Lounge", "charlie","The production on 'GNX' is on another level."),
    ("Music Lounge", "bob",    "Anyone going to a live show this summer?"),
    # Daily Wellness
    ("Daily Wellness", "bob",    "Cold showers in the morning sound brutal but they're genuinely effective."),
    ("Daily Wellness", "alice",  "Give it two weeks and you won't want to go back. Great for focus."),
    ("Daily Wellness", "charlie","Journaling for 5 minutes before bed has helped me sleep much better."),
    ("Daily Wellness", "bob",    "I journal in the morning to set intentions — night journaling is a great idea too."),
]


class Command(BaseCommand):
    help = "Populate topics, users, rooms, and seed messages"

    def handle(self, *args, **options):
    
        topic_names = ["Technology", "Lifestyle", "Health", "Business", "Travel", "Entertainment", "Education"]
        topic_map = {}
        for name in topic_names:
            obj, created = Topic.objects.get_or_create(topic=name)
            topic_map[name] = obj
            self.stdout.write(self.style.SUCCESS(f"Topic: {name}") if created else f"Topic exists: {name}")

        
        users_data = [
            {"username": "admin",   "email": "admin@example.com",   "is_staff": True,  "is_superuser": True},
            {"username": "Agent",   "email": "agent@example.com",   "is_staff": True,  "is_superuser": True},
            {"username": "alice",   "email": "alice@example.com",   "is_staff": False, "is_superuser": False},
            {"username": "bob",     "email": "bob@example.com",     "is_staff": False, "is_superuser": False},
            {"username": "charlie", "email": "charlie@example.com", "is_staff": False, "is_superuser": False},
        ]
        user_map = {}
        for ud in users_data:
            user, created = User.objects.get_or_create(
                username=ud["username"],
                defaults={
                    "email": ud["email"],
                    "is_staff": ud["is_staff"],
                    "is_superuser": ud["is_superuser"],
                    "is_active": True,
                },
            )
            if created:
                user.set_password("Quartz@123$")
                user.save()

                #user prof
                UserProfile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f"User created: {user.username}"))
            else:
                self.stdout.write(f"User exists: {user.username}")
            user_map[ud["username"]] = user

        agent = user_map["Agent"]


        room_map = {}
        for rd in ROOMS:
            parent = topic_map[rd["topic"]]
            room, created = Room.objects.get_or_create(
                name=rd["name"],
                defaults={
                    "description": rd["description"],
                    "parent_topic": parent,
                    "topic": rd["topic"],
                    "tags": rd["tags"],
                    "author": agent,
                    "is_private": False,
                },
            )
            if created:
                room.members.add(agent, user_map["alice"], user_map["bob"], user_map["charlie"])
                try:
                    add_room(room)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"ChromaDB skipped for '{room.name}': {e}"))
                self.stdout.write(self.style.SUCCESS(f"Room created: {room.name}"))
            else:
                self.stdout.write(f"Room exists: {room.name}")
            RoomModerationType.objects.get_or_create(room=room, defaults={"moderation_type": -2})
            room_map[rd["name"]] = room

        # ── Messages ─────────────────────────────────────────────────────────
        for room_name, username, text in MESSAGES:
            room = room_map.get(room_name)
            author = user_map.get(username)
            if not room or not author:
                continue
            _, created = Message.objects.get_or_create(
                room=room,
                author=author,
                message=text,
                defaults={"is_moderated": True},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  [{room_name}] {username}: {text[:60]}"))
            else:
                self.stdout.write(f"  Message exists in {room_name}")

        self.stdout.write(self.style.SUCCESS("\nPopulation complete."))
