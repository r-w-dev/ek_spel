# WKspel 2022


## Installatie
  - Installeer python >= `3.10`
     - https://www.python.org/downloads/
  - Maak een virtualenv: `python3 -m venv venv_wkspel` en zorg dat deze geactiveerd is
  - Download wheel: https://github.com/r-w-dev/ek_spel/releases
  - Installeer release, bv: `pip install wkspel2022-0.5.0-py2.py3-none-any.whl`
    - Download ook programma xlsx
  - Gebruik via de command line: `wkspel2022`


```
usage: wkspel2022 [-h] {create,load,update,print,dump} ...

WKspel 2002 application

positional arguments:
  {create,load,update,print,dump}
    create              Migrate tables into the database
    load                Initial load of all data
    update              Update operations on tables
    print               print statistics
    dump                Dump to file

options:
  -h, --help            show this help message and exit

Have fun!
```

## Gebruik
1. Specificeer altijd database in `CONNECTION_STRING` environment variabele
2. Run `wkspel2022 create`
3. Run `wkspel2022 load --source_file=<programma xlsx> --invullijsten=<map met lijsten>`
   - Lijsten die met een underscore `_` beginnen, worden genegeerd
4. Update scores in programma, daarna `wkspel2022 update --source_file=<programma xlsx>`
5. Update `final_mapper.json` in dezelfde map als waar het programma staat
6. `wkspel2022 print`
