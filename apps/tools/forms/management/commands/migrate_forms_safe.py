from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Safely migrate forms app - handles existing tables'

    def handle(self, *args, **options):
        self.stdout.write('Checking forms tables...')
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'forms'
                );
            """)
            forms_exists = cursor.fetchone()[0]
            
            if forms_exists:
                self.stdout.write(self.style.WARNING('Forms tables already exist. Marking migration as applied...'))
                from django.core.management import call_command
                call_command('migrate', 'tools_forms', '0001', '--fake', verbosity=0)
                self.stdout.write(self.style.SUCCESS('Migration marked as applied'))
            else:
                self.stdout.write('Tables do not exist. Running migration...')
                from django.core.management import call_command
                call_command('migrate', 'tools_forms', verbosity=2)
                self.stdout.write(self.style.SUCCESS('Migration completed'))
