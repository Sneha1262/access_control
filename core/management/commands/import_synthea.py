from django.core.management.base import BaseCommand
from core.models import Patient  # adjust if model path differs
import csv

class Command(BaseCommand):
    help = "Import patients from a Synthea-generated CSV file"

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to the Synthea patients CSV file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file']

        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                imported = 0

                for row in reader:
                    patient, created = Patient.objects.get_or_create(
                        synthea_id=row['synthea_id'],
                        defaults={
                            'given': row['given'],
                            'family': row['family'],
                            'birthdate': row['birthdate'],
                            'gender': row['gender']
                        }
                    )
                    if created:
                        imported += 1

                self.stdout.write(self.style.SUCCESS(f"✅ Imported {imported} new patients successfully."))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR("❌ File not found. Check your path."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Error: {str(e)}"))
