# dmarcReport
A Python script to convert DMARC XML reports into more human-readable files.

# Example
from dmarcReport import decompressXml,xml2table

var_input = 'c:/temp/xmlfiles/import/'

var_processed = 'c:/temp/xmlfiles/processed/'

var_output = 'c:/temp/xmlfiles/export/'

\# find any gzipped xml files and decompress them

decompressXml(var_input)

\# extract the information from the dmarc reports

xml2table(var_input, var_processed, var_output)
