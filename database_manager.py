import sqlite3
import os
import logging

# Configure logger for this module
logger = logging.getLogger(__name__)

# Define the database file name
DB_NAME = 'promotions.db'

class DatabaseManager:
    """
    Manages all SQLite database operations for sources and posts.
    """
    def __init__(self, db_name: str = DB_NAME):
        self.db_name = db_name
        self._create_database_and_tables()

    def _get_connection(self):
        """Helper to get a database connection."""
        return sqlite3.connect(self.db_name)

    def _create_database_and_tables(self):
        """
        Creates an SQLite database and tables to store source information,
        post titles, and links, designed for multiple sources.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Create sources table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create posts table with a foreign key to sources
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    link TEXT UNIQUE NOT NULL,
                    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_processed INTEGER DEFAULT 0 NOT NULL,
                    FOREIGN KEY (source_id) REFERENCES sources(id)
                )
            ''')
            conn.commit()
            logger.info(f"Database '{self.db_name}' and tables 'sources' and 'posts' ensured to exist.")
        except sqlite3.Error as e:
            logger.error(f"Database error during table creation: {e}", exc_info=True)
        finally:
            if conn:
                conn.close()

    def get_or_create_source_id(self, source_name: str) -> int:
        """
        Retrieves the ID of an existing source or creates a new one if it doesn't exist.
        Returns the source ID.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Try to get existing source ID
            cursor.execute("SELECT id FROM sources WHERE name = ?", (source_name,))
            result = cursor.fetchone()

            if result:
                logger.debug(f"Source '{source_name}' already exists with ID: {result[0]}.")
                return result[0]
            else:
                # If source does not exist, insert it
                cursor.execute("INSERT INTO sources (name) VALUES (?)", (source_name,))
                conn.commit()
                source_id = cursor.lastrowid
                logger.info(f"New source '{source_name}' added to the database with ID: {source_id}.")
                return source_id
        except sqlite3.Error as e:
            logger.error(f"Database error getting/creating source '{source_name}': {e}", exc_info=True)
            return -1 # Indicate an error
        finally:
            if conn:
                conn.close()

    def insert_posts(self, source_id: int, posts: list[dict]):
        """
        Inserts a list of posts into the SQLite database, associating them with a source ID.
        Handles duplicate links by ignoring them.
        New posts are inserted with is_processed = 0 (false).
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            inserted_count = 0
            for post in posts:
                try:
                    cursor.execute(
                        "INSERT INTO posts (source_id, title, link) VALUES (?, ?, ?)",
                        (source_id, post['title'], post['link'])
                    )
                    inserted_count += 1
                except sqlite3.IntegrityError:
                    logger.info(f"Skipping duplicate post (link already exists): {post['link']}")
                except Exception as e:
                    logger.error(f"Error inserting post {post['link']}: {e}", exc_info=True)
            conn.commit()
            logger.info(f"Successfully inserted {inserted_count} new posts into '{self.db_name}'.")
        except sqlite3.Error as e:
            logger.error(f"Database error during post insertion: {e}", exc_info=True)
        finally:
            if conn:
                conn.close()

    def mark_post_as_processed(self, post_id: int):
        """
        Updates a post's 'is_processed' status to 1 (true) by its ID.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE posts SET is_processed = 1 WHERE id = ?",
                (post_id,)
            )
            conn.commit()
            if cursor.rowcount > 0:
                logger.info(f"Post ID {post_id} marked as processed.")
            else:
                logger.warning(f"Post ID {post_id} not found to mark as processed.")
        except sqlite3.Error as e:
            logger.error(f"Database error marking post ID {post_id} as processed: {e}", exc_info=True)
        finally:
            if conn:
                conn.close()

    def get_unprocessed_posts(self, limit: int = -1) -> list[dict]:
        """
        Retrieves posts that have not yet been processed (is_processed = 0).
        Returns a list of dictionaries with post details.
        """
        conn = None
        posts = []
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            query = "SELECT id, source_id, title, link, extracted_at FROM posts WHERE is_processed = 0"
            if limit > 0:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                posts.append({
                    'id': row[0],
                    'source_id': row[1],
                    'title': row[2],
                    'link': row[3],
                    'extracted_at': row[4]
                })
            logger.info(f"Retrieved {len(posts)} unprocessed posts.")
            return posts
        except sqlite3.Error as e:
            logger.error(f"Database error retrieving unprocessed posts: {e}", exc_info=True)
            return []
        finally:
            if conn:
                conn.close()
