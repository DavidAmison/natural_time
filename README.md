# natural_time v0.1.5
A parser for understanding date-times written in a variety of formats

WARNING: Currently in Alpha Development!!!

There are many great tools for interpreting dates and times when the format is known, however the aim of this project is to be able to interpret dates and times from much more fuzzy situations (e.g. Tomorrow afternoon at 3) as well as be able to extract the date or time from a sentence (e.g. I have an appointment at 6pm)

How to use:
  1) Import the package using: import natural_time
  2) Run the function: natural_time.natural_time("Your_String_Here")
  3) Thats it (the natural_time function returns the date as a string in the format d/m/y h:m

If you find examples of phrases that don't interpret correcly raise an issue and I'll work on incorporating it, you are welcome to also make contributions to the code.
