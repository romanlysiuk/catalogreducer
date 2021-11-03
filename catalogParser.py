import xml.etree.ElementTree as ET


class CatalogParser:
    def __init__(self, catalog_filename):
        self.cat_filename = catalog_filename
        self.cat_file = None
        self.product_dict = {}
        self.master_dict = {}
        self.cat_metadata = None
        self.header = ""
        self.required_list = []

    def parse_cat_metadata(self, reopen=False):
        if reopen or self.cat_file is None:
            self.cat_file = open(self.cat_filename, "r", encoding="utf-8")

        line = self.cat_file.readline()
        cat_metadata = {}
        while line:
            if "<catalog " in line:
                catalog = ET.fromstring(line + "</catalog>")
                cat_metadata = {"catalog-id": catalog.attrib["catalog-id"],
                                "xmlns": "http://www.demandware.com/xml/impex/catalog/2006-10-31"}
                break
            line = self.cat_file.readline()
        self.cat_metadata = cat_metadata
        return self.cat_metadata

    def parse_header(self, reopen=False):
        if reopen or self.cat_file is None:
            self.cat_file = open(self.cat_filename, "r", encoding="utf-8")

        line = self.cat_file.readline()
        while line:
            if "<header" in line:
                header = line
                while "</header" not in line:
                    line = self.cat_file.readline()
                    header += line
                break
            line = self.cat_file.readline()
        self.header = header
        return self.header

    def parse_next_product(self, reopen=False):
        if reopen or self.cat_file is None:
            self.cat_file = open(self.cat_filename, "r", encoding="utf-8")

        product = ""
        line = self.cat_file.readline()
        while line:
            if "<product " in line:
                product = line
                while "</product" not in line:
                    line = self.cat_file.readline()
                    product += line
                break
            line = self.cat_file.readline()
        return product

    @staticmethod
    def get_children(child_name, parent):
        children = []
        for child in parent:
            if child.tag == child_name:
                children.append(child)
        return children

    def set_catalog_filename(self, filename):
        self.cat_filename = filename

    def readline(self):
        return self.cat_file.readline()

    def index(self):
        self.parse_cat_metadata(True)
        self.parse_header()
        product = self.parse_next_product()
        while product:
            product_obj = ET.fromstring(product)
            product_id = product_obj.attrib["product-id"]
            if product_id not in self.product_dict:
                self.product_dict[product_id] = {
                    "product-id": product_id,
                    "variant": False,
                    "variation_group": False,
                    "master": False
                }

            variations = self.get_children("variations", product_obj)
            if len(variations):
                self.master_dict[product_id] = {"id": product_id, "variation_groups": [], "variants": []}
                self.product_dict[product_id] = {
                    "product-id": product_id,
                    "variant": False,
                    "variation_group": False,
                    "master": True
                }
                for variations_entity in variations:
                    variants = self.get_children("variants", variations_entity)
                    variation_groups = self.get_children("variation-groups", variations_entity)
                    for variants_entity in variants:
                        variant_collection = self.get_children("variant", variants_entity)
                        for variant in variant_collection:
                            variant_id = variant.attrib["product-id"]
                            self.master_dict[product_id]["variants"].append({
                                "variant": variant_id,
                                "master": product_id
                            })
                            self.product_dict[variant_id] = {
                                "product-id": variant_id,
                                "variant": True,
                                "variation_group": False,
                                "master": False,
                                "master-id": product_id
                            }

                    for variation_groups_entity in variation_groups:
                        variation_group_collection = self.get_children("variation-group", variation_groups_entity)
                        for variation_group in variation_group_collection:
                            variation_group_id = variation_group.attrib["product-id"]
                            self.master_dict[product_id]["variation_groups"].append({
                                "variation_group": variation_group_id,
                                "master": product_id
                            })
                            self.product_dict[variation_group_id] = {
                                "product-id": variation_group_id,
                                "variant": False,
                                "variation_group": True,
                                "master": False,
                                "master-id": product_id
                            }
            product = self.parse_next_product()

    def list_all_products(self):
        for product_id in self.product_dict:
            if self.product_dict[product_id]["master"]:
                print("{} is master".format(product_id))
            if self.product_dict[product_id]["variation_group"]:
                print("{} is variation group, his master is {}".format(product_id,
                                                                       self.product_dict[product_id]["master-id"]))
            if self.product_dict[product_id]["variant"]:
                print("{} is variant, his master is {}".format(product_id,
                                                               self.product_dict[product_id]["master-id"]))

    def filter(self):
        for required_product in self.required_list:
            # mark product to be included into result
            self.product_dict[required_product]["filtered"] = True
            # mark also master and all variations and variation groups
            if "master-id" in self.product_dict[required_product]:
                required_master = self.product_dict[required_product]["master-id"]
                for variant in self.master_dict[required_master]["variants"]:
                    self.product_dict[variant["variant"]]["filtered"] = True
                for variation_group in self.master_dict[required_master]["variation_groups"]:
                    self.product_dict[variation_group["variation_group"]]["filtered"] = True

    def set_required_list(self, rq_lst):
        self.required_list = rq_lst

    def generate_output(self, out_filename):
        out_file = open(out_filename, "w", encoding="utf-8")
        out_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        out_file.write('<catalog xmlns="{}" catalog-id="{}">\n'.format(self.cat_metadata["xmlns"],
                                                                     self.cat_metadata["catalog-id"]))
        out_file.write(self.header + '\n')
        product = self.parse_next_product(True)
        while product:
            product_obj = ET.fromstring(product)
            product_id = product_obj.attrib["product-id"]
            if product_id in self.product_dict and "filtered" in self.product_dict[product_id] and self.product_dict[product_id]["filtered"] is True:
                out_file.write(product + '\n')
            product = self.parse_next_product()
        out_file.write('</catalog>\n')
        out_file.close()

    def get_product_dict(self):
        return self.product_dict

    def get_master_dict(self):
        return self.master_dict
