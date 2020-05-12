from xml2json import xml2json


# to get a json string
converter = xml2json("test.xml", encoding="utf-8")
print(converter.get_json())