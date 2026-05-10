# WKspel

## Installatie
  - Installeer [Python](https://www.python.org/downloads/) niet ouder dan `3.11`
  - Activeer een [virtualenv](https://virtualenv.pypa.io/en/latest/how-to/usage.html#activate-a-virtual-environment)
    - macOS/Linux
      ```bash
      python3 -m venv venv_wkspel
      source venv_wkspel/bin/activate
      ```
    - Windows
      ```powershell
      python -m venv venv_wkspel
      .\venv_wkspel\Scripts\activate
      ```
  - Installeer release
    ```bash
    pip install git+https://github.com/r-w-dev/ek_spel.git@wkspel-2026
    ```
  - Download het WK speelschema [2026 xlsx](https://github.com/r-w-dev/ek_spel/tree/wkspel-2026/programma/2026) + [2026 final_mapper.json](https://github.com/r-w-dev/ek_spel/blob/wkspel-2026/programma/2026/final_mapper.json)
    plaats de bestanden in 'wkspel2026' map
  - Gebruik via de command line: `wkspel`

## Gebruik
1. Zorg dat je in dezelfde map staat als het speelschema en de final_mapper.json (`cd`)
2. Maak map `invullijsten` en plaats de lijsten in deze map
3. Specificeer een database in de `CONNECTION_STRING` environment variabele
    - macOS/linux:
       ```bash
       export CONNECTION_STRING="sqlite:///wkspel2026.db"`
       ```
    - Windows (powershell):
       ```powershell
      $env:CONNECTION_STRING="sqlite:///wkspel2026.db"`
      ```
   - Windows (CMD):
        ```cmd
       set CONNECTION_STRING="sqlite:///wkspel2026.db"`
       ```
4. Initialiseer
    ```bash
    # Create database
    wkspel create
    
    # load speelschema en invullijsten
    wkspel load --source_file=wk-2026-speelschema.xlsx --source_forms=invullijsten
    ```
5. Update scores in het speelschema + final_mapper.json, daarna importeer de nieuwe scores
    ```bash
    # Update scores
    wkspel update --source_file=wk-2026-speelschema.xlsx
    ```
6. (optioneel) export data
    ```bash
    # print ranking
    wkspel print_ranking
    
    # print poules
    wkspel print_poules
    
    # dump to file in current directory
    wkspel dump --table {User,Team,Ranking,Games}
    ```
