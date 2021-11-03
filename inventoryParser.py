import xml.etree.ElementTree as ET


class InventoryParser:
    def __init__(self, inventory_filename):
        self.inv_filename = inventory_filename
        self.inv_file = None
        self.header = ""

    def parse_header(self, reopen=False):
        if reopen or self.inv_file is None:
            self.inv_file = open(self.inv_filename, "r", encoding="utf-8")

        line = self.inv_file.readline()
        while line:
            if "<header" in line:
                header = line
                while "</header" not in line:
                    line = self.inv_file.readline()
                    header += line
                break
            line = self.inv_file.readline()
        self.header = header
        return self.header

    def parse_next_record(self, reopen=False):
        if reopen or self.inv_file is None:
            self.inv_file = open(self.inv_filename, "r", encoding="utf-8")

        record = ""
        line = self.inv_file.readline()
        while line:
            if "<record " in line:
                record = line
                while "</record" not in line:
                    line = self.inv_file.readline()
                    record += line
                break
            line = self.inv_file.readline()
        return record

    def generate_output(self, product_dict, out_filename):
        self.parse_header()
        out_file = open(out_filename, "w", encoding="utf-8")
        out_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        out_file.write('<inventory xmlns="http://www.demandware.com/xml/impex/inventory/2007-05-31">\n')
        out_file.write(' ' * 4 + '<inventory-list>' + '\n')
        out_file.write(self.header + '\n')
        out_file.write(' ' * 8 + '<records>' + '\n')
        record = self.parse_next_record(True)
        while record:
            record_obj = ET.fromstring(record)
            product_id = record_obj.attrib["product-id"]
            if product_id in product_dict and "filtered" in product_dict[product_id] and product_dict[product_id]["filtered"] is True:
                out_file.write(record + '\n')
            record = self.parse_next_record()
        out_file.write(' ' * 8 + '</records>' + '\n')
        out_file.write(' ' * 4 + '</inventory-list>' + '\n')
        out_file.write('</inventory>\n')
        out_file.close()
        