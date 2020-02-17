# Generated by Django 2.2.10 on 2020-02-14 10:58

from django.db import migrations, models

fields = ("document", "question", "slug")


def remove_duplicates(apps, schema_editor):
    DynamicOption = apps.get_model("caluma_form", "DynamicOption")
    HistoricalDynamicOption = apps.get_model("caluma_form", "HistoricalDynamicOption")
    db_alias = schema_editor.connection.alias

    # get soon-to-be unique_together values from all records
    all_options = DynamicOption.objects.using(db_alias).values(*fields).order_by()

    # group by those values; annotate with max `modified_at`
    grouped = all_options.annotate(max_modified_at=models.Max("modified_at"))

    for group in grouped:
        to_delete = DynamicOption.objects.using(db_alias).filter(
            **{x: group[x] for x in fields}
        )
        to_delete = to_delete.exclude(modified_at=group["max_modified_at"])

        historical_to_delete = HistoricalDynamicOption.objects.using(db_alias).filter(
            id__in=to_delete.values_list("id", flat=True)
        )

        historical_to_delete.delete()
        to_delete.delete()


class Migration(migrations.Migration):

    dependencies = [("caluma_form", "0028_auto_20200210_0929")]

    operations = [
        migrations.RunPython(remove_duplicates, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name="dynamicoption", unique_together={("slug", "document", "question")}
        ),
        migrations.AlterUniqueTogether(
            name="historicaldynamicoption", unique_together=set()
        ),
    ]