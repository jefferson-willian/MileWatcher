import logging
import sqlite3
from datetime import datetime
from milewatcher.common.file_config_manager import FileConfigManager

# Configure logger for this module
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages all SQLite database operations for sources and posts.
    """
    def __init__(self):
        self._db_name = FileConfigManager().get_file_path('database.db') 
        self._create_database_and_tables()

    def _get_connection(self):
        """Helper to get a database connection."""
        return sqlite3.connect(self._db_name)

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
                        processed_at TIMESTAMP,
                        is_content_relevant BOOLEAN,
                        FOREIGN KEY (source_id) REFERENCES sources(id)
                    )
                ''')
            conn.commit()
            logger.info(f"Database '{self._db_name}' and tables 'sources' and 'posts' ensured to exist.")
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
            skipped_count = 0
            for post in posts:
                try:
                    cursor.execute(
                        "INSERT INTO posts (source_id, title, link) VALUES (?, ?, ?)",
                        (source_id, post['title'], post['link'])
                    )
                    inserted_count += 1
                except sqlite3.IntegrityError:
                    skipped_count += 1
                except Exception as e:
                    logger.error(f"Error inserting post {post['link']}: {e}", exc_info=True)
            conn.commit()
            logger.info(f"Skipped {skipped_count} posts and inserted {inserted_count} new posts into '{self._db_name}'.")
        except sqlite3.Error as e:
            logger.error(f"Database error during post insertion: {e}", exc_info=True)
        finally:
            if conn:
                conn.close()

    def update_post_relevance_status(self, post_id: int, is_relevant: bool):
        """
        Sets a post's 'is_content_relevant' status and records the 'processed_at' timestamp
        with the current time.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Get the current timestamp
            current_timestamp = datetime.now().isoformat()

            cursor.execute(
                """
                UPDATE posts
                SET is_content_relevant = ?,
                    processed_at = ?
                WHERE id = ?
                """,
                (is_relevant, current_timestamp, post_id) # is_relevant (Python bool) maps to SQLite BOOLEAN
            )
            conn.commit()
            if cursor.rowcount > 0:
                logger.info(f"Post ID {post_id} marked as relevant: {is_relevant} at {current_timestamp}.")
            else:
                logger.warning(f"Post ID {post_id} not found to update relevance status.")
        except sqlite3.Error as e:
            logger.error(f"Database error updating relevance for post ID {post_id}: {e}", exc_info=True)
        finally:
            if conn:
                conn.close()

    def get_posts_for_content_processing(self, source_id: int = None, limit: int = -1) -> list[dict]:
        """
        Retrieves posts that have not yet had their content processed/assessed for relevance
        (i.e., 'is_content_relevant' is NULL).
        Returns a list of dictionaries, where each dictionary contains 'id' and 'link'.
        """
        conn = None
        posts_to_process = []
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            query = """
                SELECT id, link
                FROM posts
                WHERE is_content_relevant IS NULL
            """
            params = []
            if source_id is not None:
                query += " AND source_id = ?"
                params.append(source_id)

            if limit > 0:
                query += f" LIMIT {limit}"

            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()

            for row in rows:
                # --- CORREÇÃO APLICADA AQUI: Acessando por índice numérico ---
                posts_to_process.append({
                    'id': row[0],  # 'id' é a primeira coluna na SELECT (índice 0)
                    'link': row[1] # 'link' é a segunda coluna na SELECT (índice 1)
                })
            logger.info(f"Retrieved {len(posts_to_process)} posts requiring relevance assessment (id and link only).")
            return posts_to_process
        except sqlite3.Error as e:
            logger.error(f"Database error retrieving posts for relevance assessment: {e}", exc_info=True)
            return []
        finally:
            if conn:
                conn.close()
