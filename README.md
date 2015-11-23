A tool for filtering data from CSV files.

## Examples

### Simple selection of numeric columns

    csvtool 0:2,5,10-12 input.csv output.csv

### Simple selection of named columns

    csvtool -H id,firstname,lastname input.csv output.csv

### Ranges using named columns

    csvtool -H id-lastname input.csv output.csv

### Mixed named/numeric columns

    csvtool -H 0-2,position input.csv output.csv

### Filtered values with named columns

    csvtool -H id,firstname|capitalize,lastname|capitalize,widgets|int

### Filtered values with numeric columns

    csvtool 0,row[1]|capitalize,row[2]|capitalize

### Filtered ranges

    NotImplemented
