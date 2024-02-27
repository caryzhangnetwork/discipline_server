import os.path
import importlib
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
dbPath = os.path.join(basedir, 'disciplineDatabase.db')
dbURL = 'sqlite:///' + dbPath
engine = create_engine(dbURL, poolclass=QueuePool)


def create_all_model(app):
    with app.app_context():
        app.config['SQLALCHEMY_DATABASE_URI'] = dbURL
        db = SQLAlchemy(app)
        models = get_model_list(os.path.join(basedir, 'discipline_server', 'models'))
        if len(models) > 0:
            create_table(db, models)

        print('db running')


def create_session():
    # create a queue pool to save some connection performance
    session = sessionmaker(bind=engine)
    return session()


# get file from a path
def get_model_list(path):
    models = []
    for filepath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename != 'aColumnsDef':
                models.append(get_model(f'models.{filename}'))
    return models


def get_model(filePath):
    module_name = filePath.replace('.py', '').replace('/', '.')
    module = importlib.import_module(module_name)
    table_name = ''
    columns = ()
    if hasattr(module, 'tableName'):
        table_name = getattr(module, 'tableName')
    if hasattr(module, 'columns'):
        columns = getattr(module, 'columns')
    return {
        'tableName': table_name,
        'columns': columns
    }


def insert_column(db, element):
    columns_obj = {'id': db.Column(db.Integer, primary_key=True)}
    for column in element['columns']:
        data_type = db.Integer
        nullable = False
        if column.type == 'String':
            if column.digit and int(column.digit) > 0:
                data_type = db.String(int(column.digit))
            else:
                data_type = db.String(10)
        if column.nullable != '':
            nullable = column.nullable
        if column.foreignKey == '':
            columns_obj[column.fieldName] = db.Column(data_type, nullable=nullable)
        else:
            columns_obj[column.fieldName] = db.Column(data_type, db.ForeignKey(column.foreignKey + '.id'),
                                                      nullable=nullable)
    return columns_obj


# create table according to different models
def create_table(db, models):
    tables = []
    for element in models:
        if element['tableName'] != '':
            table_name = element['tableName']
            # check if table exist
            if not inspect(db.engine).has_table(table_name):
                columns = insert_column(db, element)
                tables.append(type(table_name, (db.Model,), columns))
    # create all the table
    for table in tables:
        if not inspect(db.engine).has_table(table.__tablename__):
            table.__table__.create(db.engine)
