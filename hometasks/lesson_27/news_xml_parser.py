"""[27] XML Parsing."""
import json

import requests
from lxml import etree

SCIPOST_XML_URL = 'https://scipost.org/atom/publications/comp-ai'
ENTRY_XPATH = '//*[local-name()="entry"]'
TAG_TITLE = 'title'
TAG_LINK = 'link'
TAG_LINK_HREF = 'href'
HTTP_TIMEOUT = 10
JSON_IDENT = 4


def parse_scipost_xml(url):
    """Parse articles xml from scipost.org resource."""
    result = []
    try:
        data = requests.get(url, timeout=HTTP_TIMEOUT)
        tree = etree.fromstring(data.text.encode('utf-8'))
        entries = tree.xpath(ENTRY_XPATH)
        for curr_entry in entries:
            entry_result = {}
            for curr_child in curr_entry.iterchildren():
                if TAG_TITLE in curr_child.tag:
                    entry_result[TAG_TITLE] = curr_child.text.strip()
                elif TAG_LINK in curr_child.tag:
                    entry_result[TAG_LINK] = curr_child.attrib[TAG_LINK_HREF]
            if text := curr_entry.xpath('text()'):
                entry_result['text'] = text[0]
            result.append(entry_result)

        return json.dumps(result, indent=JSON_IDENT)
    except Exception as g_exc:
        print(g_exc)
        return result


print(parse_scipost_xml(SCIPOST_XML_URL))
