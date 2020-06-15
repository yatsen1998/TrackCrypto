# TrackCrypto

## Description

A simple python program based on smalisca. 

It's used to track ways of function call in an apk and will generate a flow chart afterwards so analyzers can track the root of a certain method in an apk.



## How to use

1. Decompile an APK through a tool like AndroidKiller or APKtools to generate smali file directories

2. Run TrackCrypto with command like

   ```shell
   python cmd.py -f [filelocation] –db [databasename] -s [startclass] -o [outputlocation] -m [startmethod]
   ```

3. Generate the flow chart with sfdp command.



## Parameters

| Args | Functions               |
| ---- | ----------------------- |
| -f   | Smali File Location     |
| --db | Generated Database Name |
| -s   | Start Class Name        |
| -o   | Output Location         |
| -m   | Start Method Name       |



## Environment&Needed 

Built on windows10. Not tested on Linux.

1. python3.7.6
2. MySQL&SqlAlchemy
3. Graphviz



## Todo

- [ ] Add multithread to speed up the analyzing process
- [ ] Find another way to help handle the complicate image



## Notes

1. It may take about 60 mins to generate a 40M apk(that's why we need multithread).
2. It's a buggy program for my undergraduate essays so there are plenty of rooms to improve.
