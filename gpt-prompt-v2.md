I have a python class that has methods outputting pandas dataframes (`from Screener import Screener ... self.screener = Screener()`)
Your job is to write a QT5 UI for it.
Here are the specs:

# UI

## Window sketch:

---------------------------------
         Stock Screener      -[]X
---------------------------------
options [input]   options [input]
options [input]   options [input]
[    Refresh    ][    Export    ]
---------------------------------
[tab1][tab2][tab3][tab4]

            tab content

---------------------------------


## Window Description

Title: Stock Screener
Size: 800x600 default size
At the top, a series of user options, with various inputs. Displays similar to css grid if possible.
- Timeframe (list)
    - Daily
    - Monthly
- Overbought (slider, from 0 to 100)
- Oversold (slider, from 0 to 100)
- Donchian Period (Int)
- Rsi Period (Int)
- sRsi Period (Int)
- Donchian Weight (Float)
- Rsi Weight (Float)
- sRsi Weight (Float)

Under that, 2 buttons, 50% each:
- Refresh
- Export
Under that, the tabs:
    Set that dict in the code so I can set them up:
    self.tabs = {'Tab 1': my_def1, 'Tab 2': my_def2}
    When a tab is selected, it executes the def (example: my_def1), which returns the pandas dataframe to display
Under that, the tab content, taking the entire remaining space available.
This should be a table to display the dataframe.

## Behavior

If the user click refresh, you show a loading icon and disable the buttons.
You call self.screener.refresh(options) where `options` is a dict of the options of their values
When self.screener.refresh(options) is done executing, you then call the def from `self.tabs`, from the selected tab, which returns the new dataframe to display.


The code for this would be too long for your short memory & response allowance.
So in the first time, split this into multiple files and return those filenames and the name of each class.








Please write this app, only the code, no explanations, no comments in the code. Make it modular.








Please give me the code for `file.py`