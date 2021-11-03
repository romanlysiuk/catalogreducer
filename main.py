from catalogParser import CatalogParser
from inventoryParser import InventoryParser
from pricebookParser import PricebookParser
from datetime import datetime
import os

CATALOGS_SUBDIR = "/catalogs/"
INVENTORY_SUBDIR = "/inventory-lists/"
PRICEBOOKS_SUBDIR = "/pricebooks/"

base_path = input("Please enter directory name where site export is located: ")
catalogs_path = base_path + CATALOGS_SUBDIR

print("Found catalogs:")

dirnames = next(os.walk(catalogs_path), (None, [], None))[1]
print("\n".join(dirnames))
catalog_name = input("What master catalog do you need to reduce? ")

catalog_parser = CatalogParser(catalogs_path + catalog_name + "/catalog.xml")

required_str = input("Please enter list of required products(comma-separated): ")
required_list = required_str.split(",")

output_dir = input("Please enter output folder name (will be created if does not exist): ")

print("Start Time =", datetime.now().strftime("%H:%M:%S"))

catalog_parser.index()

catalog_parser.set_required_list(required_list)

catalog_parser.filter()

os.makedirs(output_dir + CATALOGS_SUBDIR + catalog_name)

catalog_parser.generate_output(output_dir + CATALOGS_SUBDIR + catalog_name + "/catalog.xml")

print("OK, catalog is done, starting process inventory lists")

os.makedirs(output_dir + INVENTORY_SUBDIR)
inventory_path = base_path + INVENTORY_SUBDIR

filenames = next(os.walk(inventory_path), (None, None, []))[2]

for inventory_filename in filenames:
    print("Inventory list '" + inventory_filename + "' in progress...")
    inventoryParser = InventoryParser(inventory_path + "/" + inventory_filename)
    inventoryParser.generate_output(catalog_parser.get_product_dict(), output_dir + INVENTORY_SUBDIR + inventory_filename)

print("Unbelievable! Inventory list are also filtered! Let's go to pricebooks")

os.makedirs(output_dir + PRICEBOOKS_SUBDIR)
pricebook_path = base_path + PRICEBOOKS_SUBDIR

filenames = next(os.walk(pricebook_path), (None, None, []))[2]

for pricebook_filename in filenames:
    print("Pricebook '" + pricebook_filename + "' in progress...")
    inventoryParser = PricebookParser(pricebook_path + "/" + pricebook_filename)
    inventoryParser.generate_output(catalog_parser.get_product_dict(), output_dir + PRICEBOOKS_SUBDIR + pricebook_filename)

print("End Time =", datetime.now().strftime("%H:%M:%S"))
print("Seems, it's done successfully. Now you can zip created folder and upload it to sandbox. Good luck!")
