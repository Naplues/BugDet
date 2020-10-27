# -*-coding:utf-8-*-
# The script has been tested successfully.

from helper.file_helper import *
from jira import JIRAError
from jira.client import JIRA


def collect_bugs(proj):
    """
    Collect Bug reports data from JIRA ITS
    """
    jira = JIRA(server="https://issues.apache.org/jira/", auth=('naplues', '211314Ting'))

    statistics_path = root_path + '/BugReport/statistics/'
    reports_path = root_path + '/BugReport/reports/' + proj + '/'
    make_path(statistics_path)
    make_path(reports_path)

    text = 'id, Key, Type, Status, Resolution, Priority, AffectsVersions, FixedVersions, Reporter, Creator,' \
           ' Assignee, CreatedDate, ResolutionDate, UpdatedDate, Summary\n'
    search_str = 'project = ' + proj.upper() + ' AND issuetype = Bug AND status in (Resolved, Closed) AND ' \
                                               'resolution in (Fixed, Resolved) ORDER BY key ASC'

    start = 0
    max_results_each_search = 1000
    while True:
        issues = jira.search_issues(search_str, startAt=start, maxResults=max_results_each_search)
        for issue in issues:
            try:
                reporter_name = 'Unassigned' if issue.fields.reporter is None else issue.fields.reporter.displayName
                creator_name = 'Unassigned' if issue.fields.creator is None else issue.fields.creator.displayName
                assignee_name = 'Unassigned' if issue.fields.assignee is None else issue.fields.assignee.displayName

                # Record each bug report information
                text += issue.id + ','
                text += issue.key + ','
                text += issue.fields.issuetype.name + ','
                text += issue.fields.status.name + ','
                text += issue.fields.resolution.name + ','
                text += issue.fields.priority.name + ','
                text += '|'.join([version.name for version in issue.fields.versions]) + ','
                text += '|'.join([version.name for version in issue.fields.fixVersions]) + ','
                text += reporter_name + ','
                text += creator_name + ','
                text += assignee_name + ','
                text += issue.fields.created + ','
                text += issue.fields.resolutiondate + ','
                text += issue.fields.updated + ','
                text += issue.fields.summary.replace('\n', ' ') + '\n'

                # Output the text content of each bug report to a file
                text_content = 'XXX Summary XXX\n' + issue.fields.summary.replace('\n', ' ') + '\nXXX Description XXX\n'
                text_content += '' if issue.fields.description is None else issue.fields.description
                save_data_to_file(reports_path + issue.key + '.txt', text_content)

            except JIRAError:
                continue
            except TypeError:
                continue
            except AttributeError:
                continue

        start += max_results_each_search
        print(start, issues.total)
        if start >= issues.total:
            break

    # Output the statistics information of the project
    save_data_to_file(statistics_path + proj + '.csv', text)
    print('The collection for bug reports of Project ' + proj + ' has finished!')


if __name__ == '__main__':

    for project in projects:
        collect_bugs(project)
