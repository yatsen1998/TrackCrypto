# -*- coding: utf-8 -*-
import os
import re
import codecs
from database import SmaliCall
import copy

class SmaliParser:

    def __init__(self,DataGenerate,sql):
        self.classes = []
        self.Datagen = DataGenerate
        #self.Graphgen = GraphGenerate()
        self.sql = sql
    def run(self,file_path):
        self.parse_location(file_path)

    def parse_location(self, file_path):
        for file_path, sub_dirs, filenames in os.walk(file_path):
            if filenames:
                # 如果是文件，则加append到list中
    
                #parse_file(filenames)
                for filename in filenames:
                    # 同时进行分析

                    check = 1#self.check_crypto(os.path.join(file_path, filename))
                    if check:
                        #print('Parsing file:'+os.path.join(file_path, filename))
                        #parse file
                        self.parse_file(os.path.join(file_path, filename))
                        #print(filename)
                        for c in self.Datagen.get_classes():
                            self.sql.add_class_db(c)

                        # Add methods
                        for m in self.Datagen.get_methods():
                            self.sql.add_method_db(m)
            
                        # Add calls
                        for c in self.Datagen.get_calls():
                            self.sql.add_call_db(c)
                                    #print(self.classes)

                        self.Datagen.clean_list()


            for sub_dir in sub_dirs:
                # 如果是目录，则递归调用该函数
                self.parse_location(sub_dir)

    def parse_file(self, filename):
        with codecs.open(filename,encoding='utf8') as f:
            current_class = None
            current_method = None
            current_line = 0
            synthetic_flag = 0

            for l in f.readlines():
                current_line += 1
                if '.class' in l:
                    match_class = self.is_class(l)
                    if match_class:
                        current_class = self.extract_class(match_class)
                        self.classes.append(current_class)

                if 'synthetic' in l:
                        synthetic_flag = 1
                elif '.method' in l and 'synthetic' not in l:

                    match_class_method = self.is_class_method(l)
                    if match_class_method:
                        m = self.extract_class_method(match_class_method,current_line)
                        current_method = m

                        current_class['methods'].append(m)


                elif 'invoke' in l and synthetic_flag != 1:
                    match_method_call = self.is_method_call(l)
                    if match_method_call:
                        m = self.extract_method_call(match_method_call)
    
                        # Add calling method (src)
                        m['src'] = current_method['name']
    
                        # Add call index
                        m['dst_line'] = current_line

                        # Add call to current method
                        current_method['calls'].append(m)

                elif '.end method' in l:
                    synthetic_flag = 0

                self.Datagen.add_class_obj(current_class)


            #print(self.Datagen.classes)

            f.close()


    def is_class(self,line):
        """Check if line contains a class definition
    
        Args:
            line (str): Text line to be checked
    
        Returns:
            bool: True if line contains class information, otherwise False
    
        """
        match = re.search("\.class\s+(?P<class>.*);", line)
        if match:
            #print("Found class: %s" % match.group('class'))
            return match.group('class')
        else:
            return None
    
    def is_class_method(self,line):
        """Check if line contains a method definition
    
        Args:
            line (str): Text line to be checked
    
        Returns:
            bool: True if line contains method information, otherwise False
    
        """
        match = re.search("\.method\s+(?P<method>.*)$", line)
        if match:
            #print("Found method: %s" % match.group('method'))
            return match.group('method')
        else:
            return None
    
    def is_method_call(self,line):
        """Check [MaÔif the line contains a method call (invoke-*)
    
        Args:
            line (str): Text line to be checked
    
        Returns:
            bool: True if line contains call information, otherwise False
    
        """
        match = re.search("invoke-\w+(?P<invoke>.*)", line)
        if match:
            #print("\t\t Found invoke: %s" % match.group('invoke'))
            return match.group('invoke')
        else:
            return None
    
    def extract_class(self,data):
        """Extract class information
    
            Args:
                data (str): Data would be sth like: public static Lcom/a/b/c
    
            Returns:
                dict: Returns a class object, otherwise None
    
        """
        class_info = data.split(" ")
    
        #print("class_info: %s" % class_info[-1].split('/')[:-1])
        c = {
            # Last element is the class name
            'name': class_info[-1],
    
            # Package name
            'package': ".".join(class_info[-1].split('/')[:-1]),
    
            # All elements refer to the type of class
            'type': " ".join(class_info[:-1]),
    
            # Methods
            'methods': []
        }
        return c
    
    def extract_class_method(self,data,line):
        """Extract class method info
    
        Args:
            data (str): Data would be sth like:
                public abstract isTrue(ILjava/lang/..;ILJava/string;)I
    
        Returns:
            dict: Returns a method object, otherwise None
    
        """
        method_info = data.split(" ")
    
        # A method looks like:
        #  <name>(<arguments>)<return value>
        m_name = method_info[-1]
        m_args = None
        m_ret = None
    
        # Search for name, arguments and return value
        match = re.search(
            "(?P<name>.*)\((?P<args>.*)\)(?P<return>.*)", method_info[-1])
    
        if match:
            m_name = match.group('name')
            m_args = match.group('args')
            m_ret = match.group('return')

        m = {
            # Method name
            'name': m_name,
    
            # Arguments
            'args': m_args,
    
            # Return value
            'return': m_ret,
    
            # Additional info such as public static etc.
            'type': " ".join(method_info[:-1]),

            'from_line': line,

            # Calls
            'calls': []
        }
    
        return m
    
    def extract_method_call(self,data):
        """Extract method call information
    
        Args:
            data (str): Data would be sth like:
            {v0}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;
    
        Returns:
            dict: Returns a call object, otherwise None
        """
        # Default values
        c_dst_class = data
        c_dst_method = None
        c_local_args = None
        c_dst_args = None
        c_ret = None

        # The call looks like this
        #  <destination class>) -> <method>(args)<return value>
        match = re.search(
            '(?P<local_args>\{.*\}),\s+(?P<dst_class>.*);->' +
            '(?P<dst_method>.*)\((?P<dst_args>.*)\)(?P<return>.*)', data)
    
        if match:
            c_dst_class = match.group('dst_class')
            c_dst_method = match.group('dst_method')
            c_dst_args = match.group('dst_args')
            c_local_args = match.group('local_args')
            c_ret = match.group('return')
    
        c = {
            # Destination class
            'to_class': c_dst_class,
    
            # Destination method
            'to_method': c_dst_method,
    
            # Local arguments
            'local_args': c_local_args,
    
            # Destination arguments
            'dst_args': c_dst_args,

            # Return value
            'return': c_ret
        }
    
        return c

class SmaliAnalyzer(SmaliParser):

    def __init__(self,db_session):
        self.db = db_session
        self.class_list = []


    def add_class_to_list(self, dst_class=1, dst_method=1):

        call_list = self.db.query(SmaliCall).filter(SmaliCall.dst_class == dst_class, SmaliCall.dst_method == dst_method)
        for item in call_list:
            node = {}


            node['from_class'] = item.from_class.__str__()
            node['from_method'] = item.from_method.__str__()
            node['from_line'] = item.from_line.__str__()
            node['local_args'] = item.local_args.__str__()
            node['dst_class'] = item.dst_class.__str__()
            node['dst_method'] = item.dst_method.__str__()
            node['dst_line'] = item.dst_line.__str__()


            cmp = self.check_duplicate(node)
            if not cmp:
                #print(node)
                self.class_list.append(copy.deepcopy(node))


            if cmp:
                return
            # match = operator.eq(item.from_class, item.dst_class)
            # if match:
            #     print("\n")
            #     return
            self.add_class_to_list(item.from_class, item.from_method)
        return
        #return print('end')

    def check_duplicate(self, node):
        if self.class_list == None:
            return False
        for item in self.class_list:
            match = self.check_eq(node, item)
            if match:
                return True
        return False

    def check_eq(self, a, b):
        if a['from_class'] == b['from_class'] and a['from_method'] == b['from_method'] and a['from_line'] == b['from_line'] and a['local_args'] == b['local_args'] and a['dst_class'] == b['dst_class'] and a['dst_method'] == b['dst_method'] and a['dst_line'] == b['dst_line']:
            return True
        return False

    def get_class_list(self):
        return self.class_list

# if __name__ == "__main__":
#     Datagen = DataGenerate()

#     sql = SQLModel('test')
#     #parser = SmaliParser(Datagen,sql)
#     #parser.run('D:\\python_workspace\\ads')



#     startClass1="Ljavax/crypto/spec/SecretKeySpec"
#     # startClass2="Ljavax/crypto/spec/IvParameterSpec"
#     analyzer = SmaliAnalyzer(sql.get_session())
#     analyzer.add_class_to_list(startClass1,'<init>')

#     Graphgen = Drawer(analyzer.get_class_list())
#     Graphgen.run()