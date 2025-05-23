"""
Database Connection Pooling Module

This module provides optimized database connection handling for
LLMPageRank API endpoints with connection pooling to handle
increased partner traffic efficiently.
"""

import os
import time
import logging
import psycopg2
import psycopg2.pool
import psycopg2.extras
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection pool
connection_pool = None
MAX_CONNECTIONS = 30  # Maximum connections in the pool
MIN_CONNECTIONS = 5   # Minimum connections to maintain in the pool

def initialize_connection_pool():
    """Initialize the database connection pool."""
    global connection_pool
    
    if connection_pool is not None:
        logger.info("Connection pool already initialized")
        return connection_pool
    
    try:
        # Get database URL from environment
        database_url = os.environ.get("DATABASE_URL")
        
        if not database_url:
            logger.error("DATABASE_URL environment variable not set")
            return None
        
        logger.info("Initializing database connection pool")
        
        # Create connection pool
        connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=MIN_CONNECTIONS,
            maxconn=MAX_CONNECTIONS,
            dsn=database_url
        )
        
        logger.info(f"Created connection pool with min={MIN_CONNECTIONS}, max={MAX_CONNECTIONS}")
        
        return connection_pool
    except Exception as e:
        logger.error(f"Error initializing connection pool: {e}")
        return None

def get_connection():
    """
    Get a connection from the pool.
    
    Returns:
        Database connection from the pool
    """
    global connection_pool
    
    # Initialize pool if needed
    if connection_pool is None:
        initialize_connection_pool()
    
    try:
        # Get connection from pool
        connection = connection_pool.getconn()
        logger.debug("Obtained connection from pool")
        return connection
    except Exception as e:
        logger.error(f"Error getting connection from pool: {e}")
        
        # Try to reinitialize the pool
        logger.info("Attempting to reinitialize connection pool")
        connection_pool = None
        initialize_connection_pool()
        
        # Try again
        try:
            connection = connection_pool.getconn()
            logger.debug("Obtained connection from reinitialized pool")
            return connection
        except Exception as e2:
            logger.error(f"Error getting connection after reinitializing pool: {e2}")
            return None

def release_connection(connection):
    """
    Release a connection back to the pool.
    
    Args:
        connection: Database connection to release
    """
    global connection_pool
    
    if connection_pool is None or connection is None:
        return
    
    try:
        connection_pool.putconn(connection)
        logger.debug("Released connection back to pool")
    except Exception as e:
        logger.error(f"Error releasing connection back to pool: {e}")

def execute_query(query: str, params: Optional[tuple] = None, fetch_one: bool = False, 
                dict_cursor: bool = False, commit: bool = True):
    """
    Execute a database query with automatic connection handling.
    
    Args:
        query: SQL query to execute
        params: Query parameters
        fetch_one: Whether to fetch only one result
        dict_cursor: Whether to use a dictionary cursor
        commit: Whether to commit the transaction
        
    Returns:
        Query results or row count for DML statements
    """
    connection = None
    cursor = None
    
    try:
        connection = get_connection()
        
        if connection is None:
            logger.error("Failed to get database connection")
            return None
        
        # Create cursor
        if dict_cursor:
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            cursor = connection.cursor()
        
        # Execute query
        cursor.execute(query, params)
        
        # Handle query results
        if query.strip().upper().startswith(("SELECT", "WITH")):
            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
        else:
            result = cursor.rowcount
        
        # Commit if required
        if commit:
            connection.commit()
        
        return result
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        
        # Rollback on error
        if connection is not None:
            try:
                connection.rollback()
            except Exception as rollback_error:
                logger.error(f"Error during rollback: {rollback_error}")
        
        return None
    finally:
        # Close cursor and release connection
        if cursor is not None:
            cursor.close()
        
        if connection is not None:
            release_connection(connection)

def get_pool_status():
    """
    Get the current status of the connection pool.
    
    Returns:
        Dictionary with pool status
    """
    global connection_pool
    
    if connection_pool is None:
        return {
            "initialized": False,
            "used_connections": 0,
            "available_connections": 0,
            "max_connections": MAX_CONNECTIONS,
            "min_connections": MIN_CONNECTIONS
        }
    
    try:
        # Since we can't directly access internal ThreadedConnectionPool attributes,
        # return a simpler status
        return {
            "initialized": True,
            "max_connections": MAX_CONNECTIONS,
            "min_connections": MIN_CONNECTIONS
        }
    except Exception as e:
        logger.error(f"Error getting pool status: {e}")
        return {
            "initialized": True,
            "error": str(e),
            "max_connections": MAX_CONNECTIONS,
            "min_connections": MIN_CONNECTIONS
        }

def close_all_connections():
    """Close all connections in the pool."""
    global connection_pool
    
    if connection_pool is None:
        return
    
    try:
        connection_pool.closeall()
        connection_pool = None
        logger.info("Closed all database connections in the pool")
    except Exception as e:
        logger.error(f"Error closing all connections: {e}")