import argparse
import random
import sys
import re

sys.path.append("python-dateutil-2.0/")
from dateutil.parser import parse



import sampleData
import piiLists

from tct_excel_map_reader import TctExcelMapReader

import xml.etree.ElementTree as ET


class Main:
    def __init__(self):
        self.input_tct = None
        self.input_data_file_to_be_scrubbed = None
        # self.input_tct_workbook
        # self.input_tct_worksheet
        self.tct_map = None
        self.element_tree = None


    def run(self):
        # Retrieve the command line arguments

        self.parser = argparse.ArgumentParser(description='ur mum')
        self.parser.add_argument('input_tct', nargs='?', help='tct mapping file name')
        self.parser.add_argument('input_data_file_to_be_scrubbed', nargs='?', help='which dirty, musty stank file needs a scrubbn\'')
        self.parser.add_argument('--output', help='output file name')
        args = self.parser.parse_args()

        input_tct = args.input_tct
        input_data_file_to_be_scrubbed = args.input_data_file_to_be_scrubbed


        if not input_tct and not input_data_file_to_be_scrubbed:
            input_tct = input('Enter filename of tct mapping excel file: ')
            input_data_file_to_be_scrubbed = input('Enter the  name of the data file to scrub: ')
        elif not input_tct or not input_data_file_to_be_scrubbed:
            self.parser.error('Both input_tct and input_data_file_to_be_scrubbed are required arguments')


        print(args.input_tct)
        print(args.input_data_file_to_be_scrubbed)
        print(args.output)


        read_in = TctExcelMapReader('Nevada DPS Mapping FIXED.xlsx')
        self.tct_map = read_in.read_excel()

        #TODO argument validation
        print("cheese")

        et = ET.parse('LH6P262021021600_CARFAX_NHP200700033.xml')

        for child in et.getroot():
            self.cheeseTime(child)

        et.write('output2.xml')

###########################################
        ###################
    def is_date(string, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.

        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        try:
            parse(string, fuzzy=fuzzy, ignoretz=True)
            return True

        except ValueError:
            return False

    def check_for_keyword(self, value, keyword_list):
        pattern = "|".join(keyword_list)
        regex = re.compile(pattern, re.IGNORECASE)
        return bool(regex.search(value))

    def scrubTub(self, inputNode):
        # TODO check if parent tags are in the keyword list

        for pattern in piiLists.strictPiiList:

            if self.check_for_keyword(inputNode.tag, piiLists.strictPiiList):
                return "PII DETECTED"
            else:
                return None

    def cheeseTime(self, child):
        for grandchild in child:
            self.cheeseTime(grandchild)

        # checking that the current tag is not a parent tag wrapper because there is no text value to replace
        if len(child) <= 0:
            # if tag is special tag, aka data we want to capture as per the tct mapping, we want to scramble the data so
            # that it's still meaningful
            if self.contains_special_tags(child.tag):
                child.text = self.scrubSpecial(child)
            else:
                resultScrub = self.scrubTub(child)
                if resultScrub != None:
                    child.text = (resultScrub)

    def contains_special_tags(self, tag):
        return tag in self.tct_map.values()

    def scrubSpecial(self, inputNode):
        # because we cannont call upper on Nonetype
        noChange = inputNode.text
        if inputNode.tag == self.tct_map.get("Agency_ORI"):
            return noChange
        elif inputNode.tag == self.tct_map.get("First_Name") or self.tct_map.get("Last_name"):
            return random.choice(sampleData.nameSamples)
        elif inputNode.tag == self.tct_map.get("Crash_Date"):
            return noChange
        elif inputNode.tag == self.tct_map.get("Vin"):
            return random.choice(sampleData.vinSamples)
        elif inputNode.tag == self.tct_map.get("Vehicle_Plate"):
            return random.choice(sampleData.plateSamples)
        elif inputNode.tag == self.tct_map.get("Plate_State"):
            return noChange

        # dates
        # cities
        # county
        # plate no

        # airbag
        # poi
        # damage
        # fire
        # towing


###########################################

# creates instance of Main and calls run
if __name__ == '__main__':
    app = Main()
    app.run()


"""
As we discussed this morning I would like you to add some more functionality to your Scrambler POC on Friday afternoon.  Specifically I would like the following:

Add support for attribute scrambling
Add a feature to not scramble or cheese certain fields. IE, we want to keep airbags, but since they are not PII leave them alone.
 
I would also like you to implement functionality to:
 
Read an EDI Java test file, source XSLT or source Java mapping file (if necessary), and test XML
Try to determine which fields are being used in the tests.
Add those fields to your TCT mapper
Randomize the test XML
Update the Java Test source file to test for the appropriate Random values
Take the updated XML & Test class and see if it will still work in EDI
 
"""



