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
        self.summaries = []
        #departments = [('ACCT','ACCOUNTING'),('AFAM','AFRO-AMERICAN STUDIES'),('AFST','AFRICAN STUDIES PROGRAM'),('AMES','ASIAN & MIDDLE EASTERN STUDIES'),('ANCH','ANCIENT HISTORY'),('ANTH','ANTHROPOLOGY'),('ARCH','ARCHITECTURE'),('ARTH','ART HISTORY'),('ASAM','ASIAN AMERICAN STUDIES'),('ASTR','ASTRONOMY'),('BCHE','BIOCHEMISTRY (UNDERGRADS)'),('BE','BIOENGINEERING'),('BIBB','BIOLOGICAL BASIS OF BEHAVIOR'),('BIOH','BIOETHICS'),('BIOL','BIOLOGY'),('BPUB','BUSINESS & PUBLIC POLICY'),('CHE','CHEMICAL & BIOMOLECULAR ENGR'),('CHEM','CHEMISTRY'),('CIS','COMPUTER AND INFORMATION SCI'),('CIT','COMPUTER AND INFORMATION TECH'),('CLST','CLASSICAL STUDIES'),('COLL','COLLEGE'),('COML','COMPARATIVE LITERATURE'),('COMM','COMMUNICATIONS'),('CSE','COMPUTER SCIENCE ENGINEERING'),('DEMG','DEMOGRAPHY'),('DTCH','DUTCH'),('EAS','ENGINEERING & APPLIED SCIENCE'),('ECON','ECONOMICS'),('EE','ELECTRICAL ENGINEERING'),('EEUR','EAST EUROPEAN'),('ENGL','ENGLISH'),('ENM','ENGINEERING MATHEMATICS'),('ENVS','ENVIRONMENTAL STUDIES'),('FILM','CINEMA STUDIES'),('FNAR','FINE ARTS'),('FNCE','FINANCE'),('FOLK','FOLKLORE'),('FREN','FRENCH'),('FRSM','NON-SAS FRESHMAN SEMINAR'),('GAFL','GOVERNMENT ADMINISTRATION'),('GENH','GENERAL HONORS'),('GEOL','GEOLOGY'),('GLAW','GENERAL HONORS-LAW'),('GMED','GENERAL HONORS-MEDICINE'),('GREK','GREEK'),('GRMN','GERMANIC LANGUAGES'),('HCMG','HEALTH CARE MANAGEMENT'),('HIST','HISTORY'),('HSOC','HEALTH & SOCIETIES'),('HSSC','HISTORY & SOCIOLOGY OF SCIENCE'),('INSR','INSURANCE AND RISK MANAGEMENT'),('INTR','INTERNATIONAL RELATIONS'),('ITAL','ITALIAN'),('JWST','JEWISH STUDIES PROGRAM'),('LATN','LATIN'),('LGST','LEGAL STUDIES & BUSINESS ETHICS'),('LING','LINGUISTICS'),('MATH','MATHEMATICS'),('MEAM','MECH ENGR AND APPLIED MECH'),('MGMT','MANAGEMENT'),('MKTG','MARKETING'),('MSE','MATERIALS SCIENCE AND ENGINEER'),('MUSC','MUSIC'),('NURS','NURSING'),('OPIM','OPERATIONS AND INFORMATION MGMT'),('PHIL','PHILOSOPHY'),('PHYS','PHYSICS'),('PPE','PHILOSOPHY, POLITICS, ECONOMICS'),('PRTG','PORTUGUESE'),('PSCI','POLITICAL SCIENCE'),('PSYC','PSYCHOLOGY'),('REAL','REAL ESTATE'),('RELS','RELIGIOUS STUDIES'),('RUSS','RUSSIAN'),('SARS','SOUTH ASIA REGIONAL STUDIES'),('SCND','SCANDINAVIAN'),('SLAV','SLAVIC'),('SOCI','SOCIOLOGY'),('SPAN','SPANISH'),('STAT','STATISTICS'),('SYS','SYSTEMS ENGINEERING'),('TCOM','TELECOMMUNICATIONS & NETWORKING'),('THAR','THEATRE ARTS'),('URBS','URBAN STUDIES'),('WHMP','WHARTON MANAGEMENT PROGRAM'),('WSTD','WOMEN\'S STUDIES'),('LTAM',''),('AAMW',''),('INSC',''),('CAMB',''),('TRAN',''),('ROML','ROMANCE LANGUAGES'),('EDUC',''),('LARP','LANDSCAPE ARCH & REGIONAL PLAN'),('CPLN','CITY PLANNING'),('SWRK',''),('WH','WHARTON UNDERGRADUATE'),('BMB',''),('COGS','COGNITIVE SCIENCE'),('PUBH',''),('BSTA',''),('HSPV',''),('GCB',''),('VLST','VISUAL STUDIES'),('LGIC',''),('BENF','BENJAMIN FRANKLIN SEMINARS'),('BFMD','BENJAMIN FRANKLIN SEMINARS-MED'),('CBE','CHEMICAL & BIOMOLECULAR ENGR'),('ESE','ELECTRIC & SYSTEMS ENGINEERING'),('CRIM','CRIMINOLOGY'),('LAW',''),('BIOE',''),('INTS','INTERNATIONAL STUDIES'),('AFRC','AFRICANA STUDIES'),('ALAN','ASIAN LANGUAGES'),('ANEL','ANCIENT NEAR EAST LANGUAGES'),('ARAB','ARABIC'),('BFLW','BENJAMIN FRANKLIN SEMINARS-LAW'),('CHIN','CHINESE'),('EALC','EAST ASIAN LANGUAGES & CIVILZTN'),('HEBR','HEBREW'),('JPAN','JAPANESE'),('KORN','KOREAN'),('NELC','NEAR EASTERN LANGUAGES & CIVLZT'),('PERS','PERSIAN'),('TURK','TURKISH'),('LALS','LATIN AMERICAN & LATINO STUDIES'),('SAST','SOUTH ASIA STUDIES'),('BIOT','BIOTECHNOLOGY'),('CINE','CINEMA STUDIES'),('LSMP','LIFE SCIENCES MANAGEMENT PROG'),('YDSH','YIDDISH'),('ANCS',''),('STSC','SCIENCE, TECHNOLOGY & SOCIETY'),('PSSA','SUMMER SCIENCE ACADEMY'),('GSOC','GENDER, CULTURE & SOCIETY'),('GUJR','GUJARATI'),('HIND','HINDI'),('IPD','INTEGRATED PRODUCT DESIGN'),('MGEC','MANAGEMENT OF ECONOMICS'),('MLA','MASTER OF LIBERAL ARTS PROGRAM'),('MMP','MASTER OF MEDICAL PHYSICS'),('PUNJ','PUNJABI'),('SKRT','SANSKRIT'),('TAML','TAMIL'),('TELU','TELUGU'),('URDU','URDU'),('WHCP','WHARTON COMMUNICATION PGM'),('WRIT','WRITING PROGRAM'),('AMCS',''),('BENG','BENGALI'),('BRYN','BRYN MAWR EXCHANGE'),('DYNM','ORGANIZATIONAL DYNAMICS'),('NGG',''),('HPR',''),('GSWS','GENDER,SEXUALITY & WOMEN\'S STUD'),('INTG','INTEGRATED STUDIES'),('MKSE','MARKETING & SOCIAL SYSTEMS'),('MLYM','MALAYALAM'),('BEPP','BUSINESS ECON & PUBLIC POLICY'),('MSSP','SOCIAL POLICY'),('VIPR','VIPER'),('MED','MEDICAL'),('ENGR','ENGINEERING'),('NETS','NETWORKED AND SOCIAL SYSTEMS'),('NANO','NANOTECHNOLOGY'),('PHRM','PHARMACOLOGY'),('NPLD','NONPROFIT LEADERSHIP'),('VCSN','VETERINARY CLINICAL STUDIES')]


    def add_arguments(self, parser):
        parser.add_argument("path", nargs="+", help="The path where the ISC SQL files are located.")

    def handle(self, *args, **options):
        src = "".join(options["path"])
        if not os.path.isdir(src):
            raise CommandError("The directory '{}' does not exist!".format(src))
        self.courses = self.parse(src, "test.sql")
        self.crosslistings = self.parse(src, "TEST_PCR_CROSSLIST_SUMMARY_V.sql")
        self.ratings = self.parse(src, "TEST_PCR_RATING_V.sql")
        self.summaries =self.parse(src, "TEST_PCR_SUMMARY_V.sql")
        #self.stdout.write(self.style.SUCCESS('Successfully imported data!'))

    def parse(self, src, sql_in):
        filename = "{}/" + sql_in
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
                            #values = "(" + values + ")"
                            dicts.append(self.create_dictionaries(col_names, values))
        for item in dicts:
            print(item)

    def create_dictionaries(self, col_names, values):
        entry_dict = {}

        left = col_names.index('(')
        right = col_names.index(')')
        col_names = col_names[left + 1:right]
        col_names = " ".join(col_names.split())
        col_list = col_names.split(', ')
        col_list = [name.replace("'", "") for name in col_names.split(', ')]

        value_list = re.findall(r"(?:'(.*?)'|([\d.-]+))(?:,|$)", values)
        value_list = [next(x for x in item if x) for item in value_list]
        value_list = [value.strip() for value in value_list]

        for i in range(len(value_list)):
           entry_dict[col_list[i]] = value_list[i]
        return entry_dict

    def populate_models(self):
        for course, entries in self.courses:
            entries.sort()
            desc = ""
            for num, paragraph in entries:
                desc += paragraph + "\n"
