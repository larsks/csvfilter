A tool for selecting columns from a CSV file.

## Why not awk?

Because awk doesn't handle things like quoted strings that contain
your field separator, or fields that contain embedded newlines, etc.
Consider the following simple input:

    id,name,description
    1,widget,"This is a really
    awesome widget"
    2,gadget,"If you have a widget,
    then you need a gadget"

With `csvfilter`, extracting the description is easy:

    $ csvfilter -H description < sample.csv
    description
    "This is a really
    awesome widget"
    "If you have a widget,
    then you need a gadget"

## Column selection

- `*` -- all columns
- `%` -- all columns that were not selected explicitly by
  name or number

## Examples

The following examples all assume the following input data:

    id,header1,header2,header3,header4,header5
    row1,col1,col2,col3,col4,col5
    row2,col1,col2,col3,col4,col5
    row3,col1,col2,col3,col4,col5

### Simple selection using numeric columns

    $ csvfilter 0,1,2 < sample.csv
    id,header1,header2
    row1,col1,col2
    row2,col1,col2
    row3,col1,col2

### Range selection using numeric columns

    $ csvfilter 0-2 < sample.csv
    id,header1,header2
    row1,col1,col2
    row2,col1,col2
    row3,col1,col2

### Simple selection using named columns

    $ csvfilter -H id,header2 < sample.csv
    id,header2
    row1,col2
    row2,col2
    row3,col2

### Range selection using named columns

    $ csvfilter -H header3-header5 < sample.csv
    header3,header4,header5
    col3,col4,col5
    col3,col4,col5
    col3,col4,col5

### Mixed named/numeric columns

    $ csvfilter -H 0-2,header5 < sample.csv
    id,header1,header2,header5
    row1,col1,col2,col5
    row2,col1,col2,col5
    row3,col1,col2,col5

### Reordering selected columns with %

    $ csvfilter -H header5,header2,% < sample.csv
    header5,header2,id,header1,header3,header4
    col5,col2,row1,col1,col3,col4
    col5,col2,row2,col1,col3,col4
    col5,col2,row3,col1,col3,col4

### Using filters

You can take advantage of [Jinja2 filters][] to modify column values.
Filters can be applied to single values, to ranges, or to the
aggregates `*` and `%`:

[jinja2 filters]: http://jinja.pocoo.org/docs/dev/templates/#list-of-builtin-filters

    $ csvfilter -H 'id|upper,%|title' < sample.csv
    id,header1,header2,header3,header4,header5
    ROW1,Col1,Col2,Col3,Col4,Col5
    ROW2,Col1,Col2,Col3,Col4,Col5
    ROW3,Col1,Col2,Col3,Col4,Col5
