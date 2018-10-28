import os
import sqlparse
import re

from django.core.management.base import BaseCommand, CommandError
from apps.courses.models import Course, Alias


class Command(BaseCommand):
    help = 'Import PCR data provided by ISC.'

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.courses = {}
        self.crosslistings = []
        self.ratings = []

    def add_arguments(self, parser):
        parser.add_argument("path", nargs="+", help="The path where the ISC SQL files are located.")

    def handle(self, *args, **options):
        src = "".join(options["path"])
        if not os.path.isdir(src):
            raise CommandError("The directory '{}' does not exist!".format(src))
        self.parse_course_desc(src)
        self.parse_crosslistings(src)
        self.parse_ratings(src)
        self.stdout.write(self.style.SUCCESS('Successfully imported data!'))

    def parse_course_desc(self, src):
        with open("{}/test.sql".format(src)) as f:
            statements = sqlparse.parse(f)
            for statement in statements:
                if statement.get_type() == "INSERT":
                    for token in statement.tokens:
                        if isinstance(token, sqlparse.sql.Identifier):
                            columns = re.sub(r"[()']", '', str(token))
                            columns = columns.split("\n")[1].strip()
                            col_names = columns.split(",")
                        elif isinstance(token, sqlparse.sql.Parenthesis):
                            values = re.sub(r"[()']", '', str(token))
                            value_list = values.split(",")
                            entry_tuple = (int(value_list[1]), value_list[2].strip())
                            self.courses.setdefault(value_list[0], [entry_tuple]).append(entry_tuple)
        print(self.courses)

    def parse_crosslistings(self, src):
        with open("{}/TEST_PCR_CROSSLIST_SUMMARY_V.sql".format(src)) as f:
            statements = sqlparse.parse(f)
            for statement in statements:
                if statement.get_type() == "INSERT":
                    for token in statement.tokens:
                        col_names = ["TERM", "SECTION_ID", "SUBJECT_AREA", "COURSE_NUMBER", "SECTION_NUMBER"]
                        if isinstance(token, sqlparse.sql.Parenthesis):
                            entry_dict = {}
                            values = re.sub(r"[()']", '', str(token))
                            value_list = values.split(",")
                            for i in range(len(value_list)):
                                if i < len(col_names):
                                    entry_dict[col_names[i]] = value_list[i]
                                else:
                                    entry_dict.setdefault("XLIST_SECTION", [value_list[i]]).append(value_list[i])
                            self.crosslistings.append(entry_dict)
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
                            left = col_names.index('(')
                            right = col_names.index(')')
                            col_names = col_names[left + 1:right]
                        if isinstance(token, sqlparse.sql.Parenthesis):
                            values = str(token)[1:-1]
                            values = re.sub(r'\([^)]*\)', '', values)
                            self.ratings.append(self.create_dictionaries(col_names, values))
        print(self.ratings)

    def create_dictionaries(self, col_names, values):
        entry_dict = {}
        col_names = " ".join(col_names.split())
        col_list = [name.replace("'", "") for name in col_names.split(', ')]

        values = " ".join(values.split())
        value_list = [value.strip() for value in values.split(', ')]
        for i in range(len(value_list)):
            entry_dict[col_list[i]] = value_list[i].replace("'", "")
        return entry_dict

    def populate_models(self):
        for course, entries in self.courses:
            entries.sort()
            desc = ""
            for num, paragraph in entries:
                desc += paragraph + "\n"
