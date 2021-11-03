import xml.etree.ElementTree as ET


class PricebookParser:
    def __init__(self, pricebook_filename):
        self.pricebook_filename = pricebook_filename
        self.pricebook_file = None
        self.header = ""

    def parse_header(self, reopen=False):
        if reopen or self.pricebook_file is None:
            self.pricebook_file = open(self.pricebook_filename, "r", encoding="utf-8")

        line = self.pricebook_file.readline()
        while line:
            if "<header" in line:
                header = line
                while "</header" not in line:
                    line = self.pricebook_file.readline()
                    header += line
                break
            line = self.pricebook_file.readline()
        self.header = header
        return self.header

    def parse_next_pricetable(self, reopen=False):
        if reopen or self.pricebook_file is None:
            self.pricebook_file = open(self.pricebook_filename, "r", encoding="utf-8")

        pricetable = ""
        line = self.pricebook_file.readline()
        while line:
            if "<price-table " in line:
                pricetable = line
                while "</price-table" not in line:
                    line = self.pricebook_file.readline()
                    pricetable += line
                break
            line = self.pricebook_file.readline()
        return pricetable

    def generate_output(self, product_dict, out_filename):
        self.parse_header()
        out_file = open(out_filename, "w", encoding="utf-8")
        out_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        out_file.write('<pricebooks xmlns="http://www.demandware.com/xml/impex/pricebook/2006-10-31">\n')
        out_file.write(' ' * 4 + '<pricebook>' + '\n')
        out_file.write(self.header + '\n')
        out_file.write(' ' * 8 + '<price-tables>' + '\n')
        pricetable = self.parse_next_pricetable(True)
        while pricetable:
            pricetable_obj = ET.fromstring(pricetable)
            product_id = pricetable_obj.attrib["product-id"]
            if product_id in product_dict and "filtered" in product_dict[product_id] and product_dict[product_id]["filtered"] is True:
                out_file.write(pricetable + '\n')
            pricetable = self.parse_next_pricetable()
        out_file.write(' ' * 8 + '</price-tables>' + '\n')
        out_file.write(' ' * 4 + '</pricebook>' + '\n')
        out_file.write('</pricebooks>\n')
        out_file.close()
        