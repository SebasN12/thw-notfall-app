"""
Database Connection Module
Verwaltet MySQL-Datenbankverbindungen für FastAPI
"""

import mysql.connector
from mysql.connector import Error, pooling
from contextlib import contextmanager
from typing import Generator
import os
from dotenv import load_dotenv

# Lade Environment Variables aus .env
load_dotenv()

# ============================================================================
# DATENBANKKONFIGURATION
# ============================================================================

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "thw_notfall_app"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "autocommit": True,  # Für THW-Projekt: Änderungen sofort persistieren
}

# ============================================================================
# CONNECTION POOL (Empfohlen für Production)
# ============================================================================

try:
    # Erstelle einen Connection Pool für bessere Performance
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="thw_pool",
        pool_size=5,
        pool_reset_session=True,
        **DB_CONFIG
    )
    print("✓ MySQL Connection Pool erstellt")
except Error as e:
    print(f"✗ Fehler beim Connection Pool: {e}")
    connection_pool = None


# ============================================================================
# DEPENDENCY INJECTION FÜR FASTAPI
# ============================================================================

def get_db_connection() -> Generator:
    """
    FastAPI Dependency: Stellt DB-Connection bereit
    
    Nutzung in Routes:
    ```python
    @app.get("/endpoint")
    async def my_endpoint(db=Depends(get_db_connection)):
        cursor = db.cursor()
        # ...
    ```
    """
    connection = None
    try:
        if connection_pool:
            # Nutze Connection Pool falls vorhanden
            connection = connection_pool.get_connection()
        else:
            # Fallback: Direktverbindung
            connection = mysql.connector.connect(**DB_CONFIG)
        
        yield connection
        
    except Error as e:
        print(f"✗ Datenbankverbindungsfehler: {e}")
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()


# ============================================================================
# SINGLETON CONNECTION (Alternative, für bestehende Services)
# ============================================================================

class DatabaseConnection:
    """
    Singleton-Klasse für Datenbankverbindung
    Wenn du lieber mit Klassen arbeiten möchtest
    """
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_connection(cls):
        """Holt oder erstellt Datenbankverbindung"""
        if cls._connection is None or not cls._connection.is_connected():
            try:
                if connection_pool:
                    cls._connection = connection_pool.get_connection()
                else:
                    cls._connection = mysql.connector.connect(**DB_CONFIG)
                print("✓ Datenbankverbindung hergestellt")
            except Error as e:
                print(f"✗ Fehler beim Verbinden zur Datenbank: {e}")
                raise
        return cls._connection

    @classmethod
    def close_connection(cls):
        """Schließt Datenbankverbindung"""
        if cls._connection and cls._connection.is_connected():
            cls._connection.close()
            cls._connection = None
            print("✓ Datenbankverbindung geschlossen")


# ============================================================================
# CONTEXT MANAGER (für Tests und Scripts)
# ============================================================================

@contextmanager
def database():
    """
    Context Manager für Datenbankverbindung
    
    Nutzung in Scripts:
    ```python
    with database() as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM erzeugnisgruppe")
        results = cursor.fetchall()
    ```
    """
    connection = None
    try:
        if connection_pool:
            connection = connection_pool.get_connection()
        else:
            connection = mysql.connector.connect(**DB_CONFIG)
        yield connection
    except Error as e:
        print(f"✗ Datenbankfehler: {e}")
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def test_connection() -> bool:
    """
    Testet die Datenbankverbindung
    
    Returns:
        True wenn erfolgreich, False sonst
    """
    try:
        with database() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
        print("✓ Datenbankverbindung erfolgreich getestet")
        return True
    except Error as e:
        print(f"✗ Datenbankverbindung fehlgeschlagen: {e}")
        return False


def execute_query(query: str, params: tuple = None) -> list:
    """
    Führt SELECT-Query aus und gibt Ergebnisse zurück
    
    Args:
        query: SQL-Query
        params: Query-Parameter (für Prepared Statements)
    
    Returns:
        Liste mit Ergebnissen
    
    Beispiel:
        results = execute_query("SELECT * FROM product WHERE id = %s", (1,))
    """
    try:
        with database() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
        return results
    except Error as e:
        print(f"✗ Query-Fehler: {e}")
        raise


def execute_update(query: str, params: tuple = None) -> int:
    """
    Führt INSERT/UPDATE/DELETE aus
    
    Args:
        query: SQL-Query
        params: Query-Parameter
    
    Returns:
        Anzahl betroffener Zeilen
    
    Beispiel:
        rows = execute_update("UPDATE stock SET quantity = %s WHERE id = %s", (100, 1))
    """
    try:
        with database() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            affected_rows = cursor.rowcount
            cursor.close()
        return affected_rows
    except Error as e:
        print(f"✗ Update-Fehler: {e}")
        raise


# ============================================================================
# .env BEISPIEL (erstelle diese Datei mit deinen Werten)
# ============================================================================

"""
# .env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=dein_passwort
DB_NAME=thw_notfall_app
"""

# ============================================================================
# BEIM APP-START AUSFÜHREN
# ============================================================================

if __name__ == "__main__":
    print("Testing database connection...")
    test_connection()
