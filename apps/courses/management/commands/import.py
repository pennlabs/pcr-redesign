import os
import sqlparse
import re

from django.core.management.base import BaseCommand, CommandError
from apps.courses.models import Course, Alias, Department, Instructor


class Command(BaseCommand):
    help = 'Import PCR data provided by ISC.'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.courses = []
        self.crosslistings = []
        self.ratings = []
        self.summaries = []

    def add_arguments(self, parser):
        parser.add_argument("path", nargs="+", help="The path where the ISC SQL files are located.")

    def handle(self, *args, **options):
        src = "".join(options["path"])
        if not os.path.isdir(src):
            raise CommandError("The directory '{}' does not exist!".format(src))
        self.courses = self.parse(src, "TEST_PCR_COURSE_DESC_V.sql")
        self.crosslistings = self.parse(src, "TEST_PCR_CROSSLIST_SUMMARY_V.sql")
        self.ratings = self.parse(src, "TEST_PCR_RATING_V.sql")
        self.summaries = self.parse(src, "TEST_PCR_SUMMARY_V.sql")
        self.create_departments()
        self.create_instructors()
        self.stdout.write(self.style.SUCCESS('Successfully imported data!'))

    def parse(self, src, sql_in):
        filename = os.path.join(src, sql_in)
        self.stdout.write("Reading from '{}'...".format(filename))
        dicts = []
        with open(filename.format(src), errors='ignore') as f:
            statements = sqlparse.parse(f)
            for statement in statements:
                col_names = ""
                if statement.get_type() == "INSERT":
                    for token in statement.tokens:
                        if isinstance(token, sqlparse.sql.Identifier):
                            col_names = str(token)
                        if isinstance(token, sqlparse.sql.Parenthesis):
                            values = str(token)[1:-1]
                            values = re.sub(r'\([^)]*\)', '\'unused_info\'', values)
                            dicts.append(self.create_dictionaries(col_names, values))
        self.stdout.write("Finished reading from '{}'!".format(filename))
        return dicts

    def create_dictionaries(self, col_names, values):
        left = col_names.index('(')
        right = col_names.rindex(')')
        col_names = col_names[left + 1:right]
        col_names = " ".join(col_names.split())
        col_list = [name.replace("'", "") for name in col_names.split(', ')]

        value_list = re.findall(r"(?:'(.*?[^'])'|([\d.-]+))(?:,|$)", values)
        value_list = [next(x for x in item if x).strip() for item in value_list]

        return {key: val for key, val in zip(col_list, value_list)}

    def create_departments(self):
        for dictionary in self.summaries:
            code = dictionary["SUBJECT_CODE"]
            name = dictionary["SUBJECT_AREA_DESC"]
            dept, _ = Department.objects.get_or_create(code=code,
                defaults={"name": name})

    def create_instructors(self):
        for dictionary in self.ratings:
            name = dictionary["INSTRUCTOR_NAME"]
            last_name, first_name = name.split(',')
            instructor, _ = Instructor.objects.get_or_create(first_name=first_name, last_name=last_name)
        print(Instructor.objects.all())

    def populate_models(self):
        for course, entries in self.courses:
            entries.sort()
            desc = ""
            for num, paragraph in entries:
                desc += paragraph + "\n"
