# -*- coding: utf-8 -*-
import argparse
import time
from smaliparser import SmaliParser, SmaliAnalyzer
from database import SQLModel
from database import DataGenerate
from graph import Drawer

def main():

    startClass1="Ljavax/crypto/spec/SecretKeySpec"
    startMethod="<init>"
    default_output="output/testoutput.gv"
    sum_t = 0.0

    cmdparser = argparse.ArgumentParser(description='TrackCrypto')   # 首先创建一个ArgumentParser对象
    cmdparser.add_argument('-f', nargs='*',type = str, metavar ='filelocation', required = True, help='Smali File location')
    cmdparser.add_argument('--db',type = str, nargs='*', default = 'test', metavar ='databasename', required = True, help ='Database Name')
    cmdparser.add_argument('-s', type = str, nargs='*', default = startClass1 , metavar = 'startclass', help = 'Start Class')
    cmdparser.add_argument('-o', type = str, nargs='*', default = default_output, metavar = 'output', help = "Ouput Location" )
    cmdparser.add_argument('-m', type = str, nargs='*', default = startMethod, metavar = 'startmethod', help = "Start Method")
    args = cmdparser.parse_args()

    #print(args)

    Datagen = DataGenerate()
    sql = SQLModel(args.db[0])

    """
    如果已经生成数据库，则可以注释掉下面这一段代码
    """

    print('Generating Database')
    time_start = time.time()
    sparser = SmaliParser(Datagen,sql)
    sparser.run(args.f[0])
    time_end = time.time()
    sum_t = (time_end - time_start)+ sum_t
    print('Database Generated. Time cost %f s'%sum_t)




    print('Start Analyzing')
    analyzer = SmaliAnalyzer(sql.get_session())
    analyzer.add_class_to_list(args.s[0],args.m[0])
    print('Analyze Complete')
    Graphgen = Drawer(analyzer.get_class_list())
    Graphgen.run(args.o[0])

if __name__ == "__main__":
    main()