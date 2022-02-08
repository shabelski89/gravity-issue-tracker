from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from gravity.models import Base
from functools import wraps


def catch_session(func):
    """Decorator for Session"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        print(f"Try calling db func: {func.__name__}")
        # logger.info("success calling db func: " + func.__name__)
        result = func(self, *args, **kwargs)
        try:
            self.session.commit()
            print(f"Success calling db func: {func.__name__}\n")
            # logger.info("success calling db func: " + func.__name__)
        except SQLAlchemyError as e:
            print(f"Error - {e}\n")
            # logger.error(e.args)
            self.session.rollback()
        finally:
            self.session.close()
        return result
    return wrapper


class DbOperator:
    """
    Class provide methods to operate with ORM
    """
    def __init__(self, db, echo=True):
        self.db = db
        self.echo = echo
        self.session = None
        self.engine = None

    def initialization(self):
        if self.db:
            self.engine = create_engine(self.db, echo=self.echo)
            if not database_exists(self.engine.url):
                create_database(self.engine.url)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()

    def create_all(self):
        if self.engine:
            Base.metadata.create_all(self.engine)

    def drop_all(self):
        if self.engine:
            Base.metadata.drop_all(self.engine, checkfirst=True)

    @catch_session
    def add(self, model):
        self.session.add(model)

    @catch_session
    def add_all(self, models: list):
        self.session.add_all(models)

    @catch_session
    def delete(self, *args, **kwargs):
        d = self.get_one(self, *args, **kwargs)
        if d:
            self.session.delete(d)

    @catch_session
    def check_exists(self, model, arg):
        if self.session.query(model).get(arg):
            return True
        return False

    @catch_session
    def get_one(self, **kwargs):
        if 'field' in kwargs and 'filter' in kwargs and 'join' in kwargs:
            return self.session.query(*kwargs['field']).join(kwargs['join']).filter(*kwargs['filter']).first()
        elif 'field' in kwargs and 'filter' in kwargs:
            # r = getattr(self.session.query(kwargs['field']).filter(*kwargs['filter']), 'first')()
            # return r
            return self.session.query(*kwargs['field']).filter(*kwargs['filter']).first()
        elif 'field' in kwargs and 'join' in kwargs:
            return self.session.query(*kwargs['field']).join(*kwargs['join']).first()
        elif 'field' in kwargs:
            return self.session.query(*kwargs['field']).first()
        else:
            return False

    @catch_session
    def get_all(self, **kwargs):
        if 'field' in kwargs and 'filter' in kwargs and 'join' in kwargs:
            return self.session.query(*kwargs['field']).join(kwargs['join']).filter(*kwargs['filter']).all()
        elif 'field' in kwargs and 'filter' in kwargs:
            return self.session.query(*kwargs['field']).filter(*kwargs['filter']).all()
        elif 'field' in kwargs and 'join' in kwargs:
            return self.session.query(*kwargs['field']).join(kwargs['join']).all()
        elif 'field' in kwargs:
            return self.session.query(*kwargs['field']).all()
        else:
            return False


