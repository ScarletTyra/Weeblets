import sqlite3


DATABASE = "bot.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def setup_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reaction_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            emoji TEXT NOT NULL,
            role_id INTEGER NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def add_reaction_role(
    guild_id,
    channel_id,
    message_id,
    emoji,
    role_id
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO reaction_roles
        (guild_id, channel_id, message_id, emoji, role_id)
        VALUES (?, ?, ?, ?, ?)
    """, (
        guild_id,
        channel_id,
        message_id,
        emoji,
        role_id
    ))

    connection.commit()
    connection.close()


def get_reaction_roles():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            guild_id,
            channel_id,
            message_id,
            emoji,
            role_id
        FROM reaction_roles
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows


def delete_reaction_roles(message_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM reaction_roles
        WHERE message_id = ?
    """, (message_id,))

    connection.commit()
    connection.close()
def get_roles_for_message(message_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT emoji, role_id
        FROM reaction_roles
        WHERE message_id = ?
    """, (message_id,))

    rows = cursor.fetchall()

    connection.close()

    return rows


def remove_role_from_message(message_id, emoji):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM reaction_roles
        WHERE message_id = ?
        AND emoji = ?
    """, (
        message_id,
        emoji
    ))

    connection.commit()
    connection.close()