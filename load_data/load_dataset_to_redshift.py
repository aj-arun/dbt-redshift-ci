from loguru import logger
from yaml import safe_load, YAMLError
from pandas import read_json, DataFrame
from bz2 import open as bz2_uncompresser
from redshift_connector import connect, Connection


FILE_PATH="data/events.jsonl.bz2"
REDSHIFT_ENV="transform_data/dbt_profile.yml"
SCHEMA_NAME="raw_data"
TABLE_NAME="event_logs"

def read_data(file_loc: str) -> DataFrame:
    """Reads the file and returns the python object

    Args:
        file_loc (str): file path 

    Returns:
        DataFrame : pandas dataframe is returned after reading the data

    Raises: None
    """
    with bz2_uncompresser(file_loc, 'rt', encoding='utf-8') as file:
        df_eidu_event_logs = read_json(file, lines=True)
        logger.info(f"Raw Data dimension: {df_eidu_event_logs.shape}")
        return df_eidu_event_logs
    
def get_db_connection(config: str) -> Connection:
    """connect to the redshift datawarehouse and returns the connection object

    Args:
        config (str): config file path

    Returns:
        Connection: returns a redshift_connector connection object for executing queries.

    Raises:
        Connection.InterfaceError: When host, username or password is incorrect, this error is raised
        Connection.ProgrammingError: When dbname does exist, this error is raised
    """

    def get_db_config(config_file: str) -> dict:
        """reads the config file and returns the parameter required for database connection

        Args:
            config_file (str): config file path

        Returns:
            dict : return the db params as a dict
        """
        with open(config_file, "r") as data:
            try:
                read_db_config = safe_load(data)
                return read_db_config["EIDU"]["outputs"]["dev"]
            except YAMLError as error:
                logger.error(f"Failed to read config yaml: {config_file}") 
                raise(error)

    db_config = get_db_config(config)
    try:
        db_conn = connect(
            host=db_config['host'],
            database=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password']
        )

        return db_conn
    except (Connection.ProgrammingError, Connection.InterfaceError) as error:
            logger.error(f"Failed to connect to redshift: {error}") 
            raise(error)

def commit_and_close_db_connection(conn: Connection):
    """commits all the transactions and closes the connection

    Args:
        conn (Connection): connection object to commit and close

    Returns: None

    Raises: None
    """
    conn.commit()
    conn.close()
    logger.info("Commited and Database Connection is closed")


if __name__ == "__main__":

    raw_data = read_data(FILE_PATH)
    db_conn = get_db_connection(REDSHIFT_ENV)
    
    with db_conn.cursor() as db_cursor:
        db_cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}")
        db_cursor.execute(f"""CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME}
            (
                type STRING,
                time TIMESTAMPTZ,
                logId STRING,
                logType STRING,
                name STRING,
                schoolId STRING,
                sessionId STRING
            )
            """
        )
        db_cursor.write_dataframe(raw_data, "raw_data.event_logs")

    commit_and_close_db_connection(db_conn)
    logger.success("Successfully loaded the data to {SCHEMA_NAME}.{TABLE_NAME}")

