from dataclasses import dataclass
from typing import Optional

from environs import Env
from sqlalchemy import URL


@dataclass
class TgBot:
    """
    Creates the TgBot object from environment variables.

    Attributes
    ----------
    token : str
        The bot token.
    use_redis : str
        If we need to use redis.
    division : str
        Division where bot will run.
    """

    token: str
    use_redis: bool

    @staticmethod
    def from_env(env: Env):
        """
        Creates the TgBot object from environment variables.
        """
        token = env.str("BOT_TOKEN")

        # @TODO Replace admin_ids with db users which have role 10
        # admin_ids = env.list("ADMINS", subcast=int)

        use_redis = env.bool("USE_REDIS")

        return TgBot(token=token, use_redis=use_redis)


@dataclass
class DbConfig:
    """
    Database configuration class.
    This class holds the settings for the database, such as host, password, port, etc.

    Attributes
    ----------
    host : str
        The host where the database server is located.
    password : str
        The password used to authenticate with the database.
    user : str
        The username used to authenticate with the database.
    main_db : str
        The name of the main database.
    ntp_achievements_db : str
        The name of the ntp achievements database.
    nck_achievements_db : str
        The name of the nck achievements database.
    """

    host: str
    user: str
    password: str

    main_db: str
    achiever_db: str

    def construct_sqlalchemy_url(
        self,
        db_name=None,
        driver="aioodbc",
    ) -> URL:
        """
        Конструирует и возвращает SQLAlchemy-ссылку для подключения к базе данных
        """
        connection_string = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={self.host};"
            f"DATABASE={db_name if db_name else self.achiever_db};"
            f"UID={self.user};"
            f"PWD={self.password};"
            f"TrustServerCertificate=yes;"
            f"MultipleActiveResultSets=yes;"
            f"Connection Timeout=30;"
            f"Command Timeout=60;"
            f"Pooling=yes;"
            f"Max Pool Size=100;"
            f"Min Pool Size=5;"
        )
        connection_url = URL.create(
            f"mssql+{driver}", query={"odbc_connect": connection_string}
        )

        return connection_url

    @staticmethod
    def from_env(env: Env):
        """
        Creates the DbConfig object from environment variables.
        """
        host = env.str("DB_HOST")
        user = env.str("DB_USER")
        password = env.str("DB_PASS")

        main_db = env.str("DB_MAIN_NAME")
        achiever_db = env.str("DB_ACHIEVER_NAME")

        return DbConfig(
            host=host,
            user=user,
            password=password,
            main_db=main_db,
            achiever_db=achiever_db,
        )


@dataclass
class Email:
    """
    Creates the Email object from environment variables.

    Attributes
    ----------
    host : str
        The host where the email server is located.
    port : int
        The port which used to connect to the email server.
    user : str
        The username used to authenticate with the email server.
    password : str
        The password used to authenticate with the email server.
    use_ssl : bool
        The use_ssl flag used to connect to the email server.
    """

    host: str
    port: int
    user: str
    password: str
    use_ssl: bool

    nck_email_addr: str
    ntp_email_addr: str

    @staticmethod
    def from_env(env: Env):
        """
        Creates the Email object from environment variables.
        """
        host = env.str("EMAIL_HOST")
        port = env.int("EMAIL_PORT")
        user = env.str("EMAIL_USER")
        password = env.str("EMAIL_PASS")
        use_ssl = env.bool("EMAIL_USE_SSL")

        nck_email_addr = env.str("NCK_EMAIL_ADDR")
        ntp_email_addr = env.str("NTP_EMAIL_ADDR")

        return Email(
            host=host,
            port=port,
            user=user,
            password=password,
            use_ssl=use_ssl,
            nck_email_addr=nck_email_addr,
            ntp_email_addr=ntp_email_addr,
        )


@dataclass
class WebApp:
    """
    Creates the WebApp object from environment variables.

    Attributes
    ----------
    host : str
        The host where the web app server is located.
    port : int
        The port which used to connect to the web app server.
    """

    host: str
    port: int

    @staticmethod
    def from_env(env: Env):
        """
        Creates the WebApp object from environment variables.
        """
        host = env.str("WEBAPP_HOST")
        port = env.int("WEBAPP_PORT")

        return WebApp(host=host, port=port)


@dataclass
class RedisConfig:
    """
    Redis configuration class.

    Attributes
    ----------
    redis_pass : Optional(str)
        The password used to authenticate with Redis.
    redis_port : Optional(int)
        The port where Redis server is listening.
    redis_host : Optional(str)
        The host where Redis server is located.
    """

    redis_pass: Optional[str]
    redis_port: Optional[int]
    redis_host: Optional[str]

    def dsn(self) -> str:
        """
        Constructs and returns a Redis DSN (Data Source Name) for this database configuration.
        """
        if self.redis_pass:
            return f"redis://:{self.redis_pass}@{self.redis_host}:{self.redis_port}/0"
        else:
            return f"redis://{self.redis_host}:{self.redis_port}/0"

    @staticmethod
    def from_env(env: Env):
        """
        Creates the RedisConfig object from environment variables.
        """
        redis_pass = env.str("REDIS_PASSWORD")
        redis_port = env.int("REDIS_PORT")
        redis_host = env.str("REDIS_HOST")

        return RedisConfig(
            redis_pass=redis_pass, redis_port=redis_port, redis_host=redis_host
        )


@dataclass
class Config:
    """
    The main configuration class that integrates all the other configuration classes.

    This class holds the other configuration classes, providing a centralized point of access for all settings.

    Attributes
    ----------
    tg_bot : TgBot
        Holds the settings related to the Telegram Bot.
    misc : Miscellaneous
        Holds the values for miscellaneous settings.
    db : Optional[DbConfig]
        Holds the settings specific to the database (default is None).
    redis : Optional[RedisConfig]
        Holds the settings specific to Redis (default is None).
    """

    tg_bot: TgBot
    db: DbConfig
    email: Email
    webapp: WebApp
    redis: Optional[RedisConfig] = None


def load_config(path: str = None) -> Config:
    """
    This function takes an optional file path as input and returns a Config object.
    :param path: The path of env file from where to load the configuration variables.
    It reads environment variables from a .env file if provided, else from the process environment.
    :return: Config object with attributes set as per environment variables.
    """

    # Create an Env object.
    # The Env object will be used to read environment variables.
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot.from_env(env),
        email=Email.from_env(env),
        db=DbConfig.from_env(env),
        webapp=WebApp.from_env(env),
        # redis=RedisConfig.from_env(env),
    )
