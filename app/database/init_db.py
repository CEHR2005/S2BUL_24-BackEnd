import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.core.security import get_password_hash
from app.models.user import User
from app.models.movie import Movie
from app.models.comment import Comment
from app.models.rating import Rating
from app.database.database import SessionLocal

# Set up logging
logger = logging.getLogger(__name__)

def create_test_users(db: Session):
    """Create test users in the database."""
    try:
        # Check if users already exist
        if db.query(User).count() > 0:
            logger.info("Users already exist, skipping creation")
            return

        # Create test users
        users = [
            User(
                id=uuid.uuid4(),
                username="admin",
                email="admin@example.com",
                password=get_password_hash("admin123"),
                first_name="Admin",
                last_name="User",
                age=30,
                gender="Male",
                country="USA",
                continent="NA",
                is_admin=True
            ),
            User(
                id=uuid.uuid4(),
                username="user1",
                email="user1@example.com",
                password=get_password_hash("user123"),
                first_name="John",
                last_name="Doe",
                age=25,
                gender="Male",
                country="UK",
                continent="EU"
            ),
            User(
                id=uuid.uuid4(),
                username="user2",
                email="user2@example.com",
                password=get_password_hash("user123"),
                first_name="Jane",
                last_name="Smith",
                age=28,
                gender="Female",
                country="Canada",
                continent="NA"
            ),
            User(
                id=uuid.uuid4(),
                username="user3",
                email="user3@example.com",
                password=get_password_hash("user123"),
                first_name="Alice",
                last_name="Johnson",
                age=22,
                gender="Female",
                country="Australia",
                continent="OC"
            ),
            User(
                id=uuid.uuid4(),
                username="user4",
                email="user4@example.com",
                password=get_password_hash("user123"),
                first_name="Bob",
                last_name="Brown",
                age=35,
                gender="Male",
                country="Germany",
                continent="EU"
            )
        ]

        db.add_all(users)
        db.commit()
        logger.info(f"Created {len(users)} test users")
        return users
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating test users: {str(e)}")
        raise

def create_test_movies(db: Session):
    """Create test movies in the database."""
    try:
        # Check if movies already exist
        if db.query(Movie).count() > 0:
            logger.info("Movies already exist, skipping creation")
            return

        # Create test movies
        movies = [
            Movie(
                id=uuid.uuid4(),
                title="The Shawshank Redemption",
                release_year=1994,
                director="Frank Darabont",
                cast=["Tim Robbins", "Morgan Freeman", "Bob Gunton"],
                genre=["Drama"],
                plot="Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
                duration=142,
                poster_url="https://example.com/shawshank.jpg",
                images=["https://example.com/shawshank1.jpg", "https://example.com/shawshank2.jpg"]
            ),
            Movie(
                id=uuid.uuid4(),
                title="The Godfather",
                release_year=1972,
                director="Francis Ford Coppola",
                cast=["Marlon Brando", "Al Pacino", "James Caan"],
                genre=["Crime", "Drama"],
                plot="The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
                duration=175,
                poster_url="https://example.com/godfather.jpg",
                images=["https://example.com/godfather1.jpg", "https://example.com/godfather2.jpg"]
            ),
            Movie(
                id=uuid.uuid4(),
                title="The Dark Knight",
                release_year=2008,
                director="Christopher Nolan",
                cast=["Christian Bale", "Heath Ledger", "Aaron Eckhart"],
                genre=["Action", "Crime", "Drama"],
                plot="When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
                duration=152,
                poster_url="https://example.com/darkknight.jpg",
                images=["https://example.com/darkknight1.jpg", "https://example.com/darkknight2.jpg"]
            ),
            Movie(
                id=uuid.uuid4(),
                title="Pulp Fiction",
                release_year=1994,
                director="Quentin Tarantino",
                cast=["John Travolta", "Uma Thurman", "Samuel L. Jackson"],
                genre=["Crime", "Drama"],
                plot="The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
                duration=154,
                poster_url="https://example.com/pulpfiction.jpg",
                images=["https://example.com/pulpfiction1.jpg", "https://example.com/pulpfiction2.jpg"]
            ),
            Movie(
                id=uuid.uuid4(),
                title="Inception",
                release_year=2010,
                director="Christopher Nolan",
                cast=["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Ellen Page"],
                genre=["Action", "Adventure", "Sci-Fi"],
                plot="A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
                duration=148,
                poster_url="https://example.com/inception.jpg",
                images=["https://example.com/inception1.jpg", "https://example.com/inception2.jpg"]
            )
        ]

        db.add_all(movies)
        db.commit()
        logger.info(f"Created {len(movies)} test movies")
        return movies
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating test movies: {str(e)}")
        raise

def create_test_comments(db: Session):
    """Create test comments in the database."""
    try:
        # Check if comments already exist
        if db.query(Comment).count() > 0:
            logger.info("Comments already exist, skipping creation")
            return

        # Get users and movies
        users = db.query(User).all()
        movies = db.query(Movie).all()

        if not users or not movies:
            logger.warning("No users or movies found, skipping comment creation")
            return

        # Create test comments
        comments = []

        # User 1 comments on Movie 1
        comments.append(
            Comment(
                id=uuid.uuid4(),
                movie_id=movies[0].id,
                user_id=users[1].id,
                text="This is one of the best movies I've ever seen. The acting is superb and the story is captivating."
            )
        )

        # User 2 comments on Movie 1
        comments.append(
            Comment(
                id=uuid.uuid4(),
                movie_id=movies[0].id,
                user_id=users[2].id,
                text="I loved this movie! The character development is amazing."
            )
        )

        # User 3 comments on Movie 2
        comments.append(
            Comment(
                id=uuid.uuid4(),
                movie_id=movies[1].id,
                user_id=users[3].id,
                text="A classic that never gets old. The cinematography is outstanding."
            )
        )

        # User 4 comments on Movie 3
        comments.append(
            Comment(
                id=uuid.uuid4(),
                movie_id=movies[2].id,
                user_id=users[4].id,
                text="Heath Ledger's performance as the Joker is legendary. One of the best villain portrayals in cinema history."
            )
        )

        # User 1 comments on Movie 4
        comments.append(
            Comment(
                id=uuid.uuid4(),
                movie_id=movies[3].id,
                user_id=users[1].id,
                text="Tarantino at his best. The non-linear storytelling is brilliant."
            )
        )

        # User 2 comments on Movie 5
        comments.append(
            Comment(
                id=uuid.uuid4(),
                movie_id=movies[4].id,
                user_id=users[2].id,
                text="Mind-bending plot with amazing visual effects. Christopher Nolan is a genius."
            )
        )

        db.add_all(comments)
        db.commit()
        logger.info(f"Created {len(comments)} test comments")
        return comments
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating test comments: {str(e)}")
        raise

def create_test_ratings(db: Session):
    """Create test ratings in the database."""
    try:
        # Check if ratings already exist
        if db.query(Rating).count() > 0:
            logger.info("Ratings already exist, skipping creation")
            return

        # Get users and movies
        users = db.query(User).all()
        movies = db.query(Movie).all()

        if not users or not movies:
            logger.warning("No users or movies found, skipping rating creation")
            return

        # Create test ratings
        ratings = []

        # Each user rates each movie
        for user in users[1:]:  # Skip admin user
            for i, movie in enumerate(movies):
                # Vary the ratings a bit
                score = 7 + (i % 4)  # Scores between 7-10

                ratings.append(
                    Rating(
                        id=uuid.uuid4(),
                        movie_id=movie.id,
                        user_id=user.id,
                        score=score
                    )
                )

        db.add_all(ratings)
        db.commit()
        logger.info(f"Created {len(ratings)} test ratings")
        return ratings
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating test ratings: {str(e)}")
        raise

def init_db():
    """Initialize the database with test data."""
    logger.info("Initializing database with test data...")
    db = SessionLocal()
    try:
        # Create test data
        create_test_users(db)
        create_test_movies(db)
        create_test_comments(db)
        create_test_ratings(db)

        logger.info("Database initialized with test data")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # Configure logging when running as a script
    logging.basicConfig(level=logging.INFO)
    init_db()
