# tpl8tr

Tpl8tr is a library that allows you to write dataclasses into files.


# How is it different from X ?
## Jinja
This is full python, you have access to the entire API, can do whatever you want with the code. We also provide a layer to validate that the values are correct before writing out which is tricky to achieve in Jinja.

## jsonnet
Tpl8tr can write any file format, not sure json. Just use one of the file formatter we provide on your top level object and voila.
