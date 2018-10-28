import os
import sqlparse
import re

from django.core.management.base import BaseCommand, CommandError
from apps.courses.models import Course, Alias


class Command(BaseCommand):
    help = 'Import PCR data provided by ISC.'

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.courses = []
        self.crosslistings = []
        self.ratings = []

    def add_arguments(self, parser):
        parser.add_argument("path", nargs="+", help="The path where the ISC SQL files are located.")

    def handle(self, *args, **options):
        src = "".join(options["path"])
        if not os.path.isdir(src):
            raise CommandError("The directory '{}' does not exist!".format(src))
        #self.parse_course_desc(src)
        self.parse_crosslistings(src)
        #self.parse_ratings(src)
        #self.stdout.write(self.style.SUCCESS('Successfully imported data!'))

    def parse_course_desc(self, src):
        with open("{}/test.sql".format(src)) as f:
            statements = sqlparse.parse(f)
            for statement in statements:
                col_names = ""
                if statement.get_type() == "INSERT":
                    for token in statement.tokens:
                        if isinstance(token, sqlparse.sql.Identifier):
                            col_names = str(token)
                        elif isinstance(token, sqlparse.sql.Parenthesis):
                            values = str(token)
                            self.courses.append(self.create_dictionaries(col_names, values))
        print(self.courses)

    def parse_crosslistings(self, src):
        with open("{}/TEST_PCR_CROSSLIST_SUMMARY_V.sql".format(src)) as f:
            statements = sqlparse.parse(f)
            for statement in statements:
                col_names = ""
                if statement.get_type() == "INSERT":
                    for token in statement.tokens:
                        if isinstance(token, sqlparse.sql.Identifier):
                            col_names = str(token)
                        if isinstance(token, sqlparse.sql.Parenthesis):
                            values = str(token)
                            self.crosslistings.append(self.create_dictionaries(col_names, values))
        print(self.crosslistings)

    def parse_ratings(self, src):
        with open("{}/TEST_PCR_RATING_V.sql".format(src)) as f:
            statements = sqlparse.parse(f)
            for statement in statements:
                col_names = ""
                if statement.get_type() == "INSERT":
                    for token in statement.tokens:
                        if isinstance(token, sqlparse.sql.Identifier):
                            col_names = str(token)
                        if isinstance(token, sqlparse.sql.Parenthesis):
                            values = str(token)[1:-1]
                            values = re.sub(r'\([^)]*\)', '\'unused_date_info\'', values)
                            values = "(" + values + ")"
                            self.ratings.append(self.create_dictionaries(col_names, values))
        for rating in self.ratings:
            print(rating)

    def create_dictionaries(self, col_names, values):
        entry_dict = {}

        left = col_names.index('(')
        right = col_names.index(')')
        col_names = col_names[left + 1:right]
        col_names = " ".join(col_names.split())
        col_list = col_names.split(', ')
        col_list = [name.replace("'", "") for name in col_names.split(', ')]

        value_list = re.findall(r"(?:'(.*?)'|([\d.-]+))(?:,|$)", values[1:-1])
        value_list = [next(x for x in item if x) for item in value_list]
        value_list = [value.strip() for value in value_list]

        for i in range(len(value_list)):
           entry_dict[col_list[i]] = value_list[i].replace("'", "")
        return entry_dict

    def populate_models(self):
        for course, entries in self.courses:
            entries.sort()
            desc = ""
            for num, paragraph in entries:
                desc += paragraph + "\n"
