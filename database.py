# -*- coding: utf-8 -*-
#Generate Database

import sqlalchemy as sql
import textwrap
from sqlalchemy import ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类:
Base = declarative_base()

# Classes <-> Methods
class_methods_table = sql.Table(
    'class_methods', Base.metadata,
    sql.Column('class_id', sql.Integer, ForeignKey('classes.id')),
    sql.Column('method_id', sql.Integer, ForeignKey('methods.id'))
)

# 定义SmaliClass对象:
class SmaliClass(Base):
    """Models a Smali class

    Attributes:
        id (integer): Primary key
        class_name (str): Name of the class
        class_type (str): Type of the class (public, abstract, etc.)
        methods (list): List of methods (:class:`SmaliMethod`)

    """
    # 表的名字:
    __tablename__ = 'classes'

    # 表的结构:
    id = sql.Column(sql.Integer, primary_key=True)
    class_name = sql.Column(sql.Text)
    class_type = sql.Column(sql.Text)
    class_package = sql.Column(sql.Text)

    #表的关系
    methods = relationship(
        'SmaliMethod', secondary=class_methods_table)

    def to_string(self):
        s = """
        :: ID: %d\n
        \t[+] Name: \t%s
        \t[+] Type: \t%s
        \t[+] package: \t%s
        """ % (
            self.id, self.class_name, self.class_type,
        )
        return textwrap.dedent(s)

    def __str__(self):
        return self.to_string()

    def __unicode__(self):
        return self.to_string()


class SmaliMethod(Base):
    """Models a Smali class method

    Attributes:
        id (integer): Primary key
        method_name (str): Name of the method
        method_type (str): Method type (public, abstract, constructor)
        method_args (str): Method arguments (e.g. Landroid/os/Parcelable;Ljava/lang/ClassLoader;)
        method_ret (str): Methods return value (Z, I, [I, etc.)
        method_class (str): The class the method belongs to
    """
    __tablename__ = "methods"

    # Fields
    id = sql.Column(sql.Integer, primary_key=True)
    method_name = sql.Column(sql.Text)
    method_type = sql.Column(sql.Text)
    method_args = sql.Column(sql.Text)
    method_ret = sql.Column(sql.Text)
    method_class = sql.Column(sql.Text)

    def to_string(self):
        s = """
        :: ID: %d\n 
        \t[+] Name: \t%s
        \t[+] Type: \t%s
        \t[+] Args: \t%s
        \t[+] Ret: \t%s
        \t[+] Class: \t%s
        """ % (self.id, self.method_name, self.method_type,
               self.method_args, self.method_ret, self.method_class)
        return textwrap.dedent(s)

    def __str__(self):
        return self.to_string()

    def __unicode__(self):
        return self.to_string()


class SmaliCall(Base):
    """Models a Smali call (invoke-*)

    Attributes:
        id (integer): Primary key
        from_class (str): Name of calling class
        from_method (str): Name of calling method
        local_args (str): Local arguments
        dst_class (str): Called class
        dst_method (str): Called method
        dst_args (str): Called args
        ret (str): Return value

    """
    __tablename__ = "calls"

    # Fields
    id = sql.Column(sql.Integer, primary_key=True)

    # Source class/method/args
    from_class = sql.Column(sql.Text)
    from_method = sql.Column(sql.Text)
    from_line = sql.Column(sql.Integer)
    local_args = sql.Column(sql.Text)

    # Destination class/method/args
    dst_class = sql.Column(sql.Text)
    dst_method = sql.Column(sql.Text)
    dst_args = sql.Column(sql.Text)
    dst_line = sql.Column(sql.Integer)

    # Return value
    ret = sql.Column(sql.Text)

    # FIXME: Add prettytable
    def to_string(self):
        s = """
        --------
        ID: \t%d

        From:
        \tClass: \t%s
        \tMethod: \t%s

        To:
        \tClass: \t%s
        \tMethod: \t%s

        Args:
        \tLocal: \t%s
        \tDest: \t%s
        --------
        """ % (self.from_class, self.from_method,self.from_line,
               self.dst_class, self.dst_method,
               self.local_args, self.dst_args,self.dst_line)

        return s

    def __str__(self):
        return self.to_string()

    def __unicode__(self):
        return self.to_string()


class SQLModel:

    def __init__(self,database):
        # 初始化数据库连接:

        self.engine = sql.create_engine('mysql+mysqlconnector://root:980815@localhost:3306/'+database)
        if not database_exists(self.engine.url):
            create_database(self.engine.url)

        print(database_exists(self.engine.url))
        Base.metadata.create_all(self.engine)
        # 创建DBSession类型:
        self.session = scoped_session(sessionmaker(
            autoflush=True, autocommit=False,
            bind=self.engine
        ))
        # 创建session对象:
        self.db = self.session()
        # # 创建新User对象:
        # new_user = SmaliClass(id='1', class_name='Test', class_type='public')
        # # 添加到session:
        # db.add(new_user)
        # # 提交即保存到数据库:
        # db.commit()
        # # 关闭session:
        # db.close()

        self.classes = {}
        self.methods = []
        self.calls = []

    def get_class_by_name(self, classname):

        classes = self.db.query(SmaliClass)
        class_obj = classes.filter(SmaliClass.class_name == classname)

        try:
            if self.db.query(class_obj.exists()):
                return class_obj.one()

        except sql.orm.exc.NoResultFound:
            print("No result found")
            return None


    def get_classes(self):
        """Returns all classes

        Returns:
            list: Return list of class objects

        """
        class_list = self.db.query(SmaliClass).all()
        for class_name in class_list:
            print(SmaliClass.class_name)

    def get_methods(self):
        """Return all methods

        Returns:
            list: Return list of method objects

        """
        return self.db.query(SmaliMethod).all()

    def get_calls(self):
        """Return all calls

        Returns:
            list: Return list of call objects

        """
        return self.db.query(SmaliCall).all()



    def add_class_db(self, class_obj):
        """Add new class

        Args:
            class_obj (dict): Class object to insert

        """
        new_class = SmaliClass(
            class_name=class_obj['name'],
            class_type=class_obj['type'],
            class_package=class_obj['package'],
        )

        # Add new class
        self.classes[class_obj['name']] = new_class
        self.db.merge(new_class)
        self.db.commit()

    def add_method_db(self, method):
        """Adds property to class

        Args:
            method (dict): Method object to insert

        """
        class_obj = self.get_class_by_name(method['class'])
        new_method = SmaliMethod(
            method_name=method['name'],
            method_type=method['type'],
            method_args=method['args'],
            method_ret=method['return'],
            method_class=method['class']
        )

        # Append new method to class
        class_obj.methods.append(new_method)

        # Add to DB
        try:
            self.db.merge(class_obj)
            self.db.commit()

        except sql.exc.IntegrityError:
            self.db.rollback()
            print("Found NOT unique values")

    def add_call_db(self, call):
        """Adds calls to class

        Args:
            call (dict): Call object to insert

        """

        # Create new call object
        new_call = SmaliCall(
            # Origin
            from_class=call['from_class'],
            from_method=call['from_method'],
            from_line=call['from_line'],
            local_args=call['local_args'],

            # Destination
            dst_class=call['to_class'],
            dst_method=call['to_method'],
            dst_args=call['dst_args'],
            dst_line=call['dst_line'],

            # Return
            ret=call['return']
        )

        # Add new call to DB
        self.db.merge(new_call)
        self.db.commit()

    def get_session(self):
        """Returns DB session

        Returns:

            Session: Returns DB session

        """
        return self.db


class DataGenerate():

    def __init__(self):
        self.classes={}

    def clean_list(self):
        self.classes.clear()

    def add_class_obj(self, class_obj):
        """Adds a previsously created class object
    
        Args:
            class_obj (dict): A dictionary containing info about class
    
        """
        self.classes[class_obj['name']] = class_obj

    def get_classes(self):
        """Return classes

        Returns:
            list: List of classes, otherwise None

        """
        data = []
        for k in self.classes.keys():
            c = self.classes[k]
            data.append({
                'name': c['name'],
                'type': c['type'],
                'package': c['package'],
            })

        return data

    def get_methods(self):
        """Return methods

        Returns:
            list: List of methods, otherwise None

        """
        data = []
        for c in self.classes.keys():
            methods = self.classes[c]['methods']
            for m in methods:
                data.append({
                    'name': m['name'],
                    'type': m['type'],
                    'args': m['args'],
                    'return': m['return'],
                    'class': c
                })

        return data

    def get_calls(self):
        """Return calls"""
        data = []
        for c in self.classes.keys():
            methods = self.classes[c]['methods']
            for m in methods:
                for invoke in m['calls']:
                    data.append({
                        'from_class': c,
                        'from_method': m['name'],
                        'from_line' : m['from_line'],
                        'local_args': invoke['local_args'],
                        'to_class': invoke['to_class'],
                        'to_method': invoke['to_method'],
                        'dst_args': invoke['dst_args'],
                        'return': invoke['return'],
                        'dst_line': invoke['dst_line'],
                        'class': c
                    })

        return data
