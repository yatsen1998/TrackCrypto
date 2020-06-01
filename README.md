# TrackCrypto

## Description

  A simple python program based on smalisca. It's used to track ways of function call in an apk and will generate a flow chart afterwards.

## Usage

1. Decompile an APK through a tool like AndroidKiller or APKtools to generate smali file directories

2. Run TrackCrypto with command like

   ```shell
   python cmd.py -f [filelocation] –db [databasename] -s [startclass] -o [outputlocation] -m [startmethod]
   ```

| Args | Functions          |
| ---- | ------------------ |
| -f   | File  location     |
| --db | Database  Name     |
| -s   | Start  Class Name  |
| -o   | Output  Location   |
| -m   | Start  Method Name |

## Environment&Needed 
Built on windows10. Not tested on Linux.

1. python3.7.6
2. MySQL&SqlAlchemy
3. Graphviz

## Notes

1. It may take about 60 mins to generate a 40M apk
2. Plenty of rooms to improve
