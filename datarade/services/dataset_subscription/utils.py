"""
This module contains utility functions that are used by the handlers, but which clutter up the readability of the
handlers. It's possible that some of this could be refactored away at a future date so that it could be put back into
the handlers, avoiding the need for a 'utils' file. Also, these could all be methods/properties on the appropriate
datarade domain models. However, keeping them at the service layer abstracts away the methods used to work with these
objects as those methods are not the concern of the domain model.
"""
from typing import TYPE_CHECKING

from bcp import BCP, Connection
from sqlalchemy import MetaData, create_engine, schema, types
from sqlalchemy.engine.url import URL

if TYPE_CHECKING:
    from datarade.domain import models


def get_sqlalchemy_metadata(database: 'models.Database', username: str = None, password: str = None) -> MetaData:
    """
    This will take a datarade Database object and credentials and return a sqlalchemy MetaData object.

    Args:
        database: the datarade Database object containing the attributes needed for a MetaData object
        username: the username for the database
        password: the password for the database

    Returns: a sqlalchemy MetaData object
    """
    driver = database.driver
    if driver == 'mssql':
        driver = 'mssql+pymssql'
    url = URL(drivername=driver,
              host=database.host,
              port=database.port,
              database=database.database_name,
              username=username,
              password=password)
    engine = create_engine(url)
    if database.schema_name is not None:
        return MetaData(bind=engine, schema=database.schema_name)
    else:
        return MetaData(bind=engine)


def get_sqlalchemy_column(field: 'models.Field') -> schema.Column:
    """
    This will convert a datarade Field object into a sqlalchemay Column object.

    Args:
        field: a datarade Field object

    Returns: a sqlalchemy Column object
    """
    if field.type == 'Boolean':
        return schema.Column(field.name, types.Boolean, comment=field.description)
    elif field.type == 'Date':
        return schema.Column(field.name, types.Date, comment=field.description)
    elif field.type == 'DateTime':
        return schema.Column(field.name, types.DateTime, comment=field.description)
    elif field.type == 'Float':
        return schema.Column(field.name, types.Float, comment=field.description)
    elif field.type == 'Integer':
        return schema.Column(field.name, types.Integer, comment=field.description)
    elif field.type == 'Numeric':
        return schema.Column(field.name, types.Numeric(18, 2), comment=field.description)
    elif field.type == 'String':
        return schema.Column(field.name, types.String, comment=field.description)
    elif field.type == 'Text':
        return schema.Column(field.name, types.Text, comment=field.description)
    elif field.type == 'Time':
        return schema.Column(field.name, types.Time, comment=field.description)


def get_bcp(database: 'models.Database', username: str = None, password: str = None) -> BCP:
    """
    This will take a datarade Database object and credentials and return a BCP object.

    Args:
        database: a datarade Database object
        username: the username for the database
        password: the password for the database

    Returns: a BCP object
    """
    conn = Connection(host=f'{database.host},{database.port}',
                      driver=database.driver,
                      username=username,
                      password=password)
    return BCP(conn)
