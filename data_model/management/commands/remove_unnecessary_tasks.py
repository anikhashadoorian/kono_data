import logging
import random

from django.core.management.base import BaseCommand
from django.db import connections
from tqdm import trange

from data_model.models import Task, Dataset

logger = logging.getLogger(__name__)
from collections import namedtuple


def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    DEFAULT_TASKS_PER_FILE_TO_KEEP = 30
    DEFAULT_REMOVAL_ITERATIONS = 1

    def add_arguments(self, parser):
        parser.add_argument('dataset_id', type=str)
        parser.add_argument('tasks_per_file_to_keep', nargs='?', type=int)
        parser.add_argument('iterations', nargs='?', type=int)
        parser.add_argument('verbose', action='store_true')

    def handle(self, *args, **options):
        dataset_id = options['dataset_id']
        tasks_per_file_to_keep = options['tasks_per_file_to_keep'] or self.DEFAULT_TASKS_PER_FILE_TO_KEEP
        iterations = options['iterations'] or self.DEFAULT_REMOVAL_ITERATIONS
        verbose = options['verbose']

        if verbose:
            logger.info(f'Start processing')

        self.remove_overflowing_nr_of_tasks(dataset_id, tasks_per_file_to_keep, iterations, verbose)

        if verbose:
            logger.info(f'Done with processing datasets')

    def remove_overflowing_nr_of_tasks(self, dataset_id, tasks_per_file_to_keep, iterations, verbose):
        dataset = Dataset.objects.get(id=dataset_id)
        task_count_before_removals = dataset.tasks.count()
        query = self.get_task_counts_for_files_sql_query(dataset_id)

        with connections['default'].cursor() as cursor:
            bar = trange(iterations, desc='Progress bar', leave=True)
            for i in bar:
                if iterations > 1 and verbose:
                    bar.set_description(f'{dataset.tasks.count()} tasks in dataset')

                files_with_task_count = self.get_task_counts_for_files(cursor, query)

                for file_with_task_count in files_with_task_count:
                    nr_of_tasks = len(file_with_task_count.task_ids)
                    nr_of_tasks_to_remove = nr_of_tasks - tasks_per_file_to_keep
                    if nr_of_tasks_to_remove < 1:
                        continue

                    task_ids_to_remove = random.sample(file_with_task_count.task_ids, nr_of_tasks_to_remove)
                    tasks_to_remove = Task.objects.filter(id__in=task_ids_to_remove, labels=None)

                    if not tasks_to_remove.exists():
                        continue

                    removed_count = tasks_to_remove.delete()[0]

                    if removed_count != nr_of_tasks_to_remove:
                        logger.warning(f'File {file_with_task_count.file}: Removed {removed_count} tasks '
                                       f'but was supposed to remove {nr_of_tasks_to_remove}')

        if verbose:
            task_count_after_removals = dataset.tasks.count()
            logger.info(
                f'After all {task_count_before_removals - task_count_after_removals} removals: dataset has {task_count_after_removals}')

    def get_task_counts_for_files(self, cursor, query):
        cursor.execute(query)
        return namedtuplefetchall(cursor)

    def get_task_counts_for_files_sql_query(self, dataset_id, limit=15):
        query = '''
                select 
                    file
                    , is_labeled
                    , count(*) as count
                    , array_agg(task_id::text) as task_ids
                    from
                    (select t.id as task_id, split_part(t.definition::text, ',', 1) file, l.id is not null as is_labeled from "Task" t
                    join "Dataset" d on t.dataset_id=d.id
                    left join "Label" l on l.task_id=t.id
                    where d.id='{dataset_id}'
                    union
                    select t.id, split_part(t.definition::text, ',', 2), l.id is not null as is_labeled from "Task" t
                    join "Dataset" d on t.dataset_id=d.id
                    left join "Label" l on l.task_id=t.id
                    where d.id='{dataset_id}')a
                    where is_labeled = FALSE
                    group by 1,2
                    order by count desc
                    limit {limit};
                '''.format(dataset_id=dataset_id, limit=limit)

        return query
