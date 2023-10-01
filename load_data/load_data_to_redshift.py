from loguru import logger
from yaml import safe_load, YAMLError
from pandas import read_json, DataFrame
from redshift_connector import connect, Connection

SCHEMA_NAME = "raw_data"
TABLE_NAME = "event_logs"
FILE_PATH = "data/events.jsonl.bz2"
REDSHIFT_ENV = "transform_data/dbt_profile.yml"


def read_data(file_loc: str) -> DataFrame:
    """Reads the file and returns the python object

    Args:
        file_loc (str): file path

    Returns:
        DataFrame : pandas dataframe is returned after reading the data

    Raises: None
    """
    df_eidu_event_logs = read_json(file_loc, lines=True)
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

        Raises:
            YAMLError: if yaml file has formatting issues
        """
        with open(config_file, "r") as data:
            try:
                read_db_config = safe_load(data)
                return read_db_config["EIDU"]["outputs"]["dev"]
            except YAMLError as error:
                logger.error(f"Failed to read config yaml: {config_file}")
                raise (error)

    db_config = get_db_config(config)
    try:
        db_conn = connect(
            host=db_config["host"],
            database=db_config["dbname"],
            user=db_config["user"],
            password=db_config["password"],
        )
        logger.info("Successfully connected to Redshift Datawarehouse")
        return db_conn
    except (Connection.ProgrammingError, Connection.InterfaceError) as error:
        logger.error(f"Failed to connect to redshift: {error}")
        raise (error)


def fetch_table_count_if_exists(db_cursor: Connection.cursor) -> int:
    """return the table count

    Args:
        db_cursor (Connection.cursor): Cursor object of connection class

    Returns:
        int: number of rows

    Raises:
        None
    """
    db_cursor.execute(f"""SELECT EXISTS (SELECT 1 FROM information_schema.tables
                    WHERE table_schema ='{SCHEMA_NAME}' 
                    AND table_name = '{TABLE_NAME}')""")
    
    if db_cursor.fetch_numpy_array().flat[0]:
        db_cursor.execute(f"SELECT COUNT(*) FROM {SCHEMA_NAME}.{TABLE_NAME} ")
        return db_cursor.fetch_numpy_array().flat[0]
    else:
        return 0


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
    db_cursor = db_conn.cursor()

    # loading data only when table does not exist
    if not fetch_table_count_if_exists(db_cursor):
        db_cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}")
        db_cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_NAME}
            (
                type TEXT,
                time TIMESTAMP,
                logId TEXT,
                logType TEXT,
                name TEXT,
                schoolId TEXT,
                sessionId TEXT
            )"""
        )
        db_cursor.write_dataframe(raw_data, f"{SCHEMA_NAME}.{TABLE_NAME}")
        logger.success(
                f"Successfully loaded the data to {SCHEMA_NAME}.{TABLE_NAME}"
            )
    else:
        logger.info(
            f"Skipping: Table already exists with data {SCHEMA_NAME}.{TABLE_NAME}"
        )

    commit_and_close_db_connection(db_conn)