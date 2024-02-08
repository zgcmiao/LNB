## Project Files

| Components       | Description                                          |
|------------------|------------------------------------------------------|
| docs             | Project documents                                    |
| src              | Project core code, contains APIs and schedules task. |
| Dockerfile       | Dockerfile                                           |
| manager.py       | Manager file                                         |
| requirements.txt | Dependent packages                                   |
| run.sh           | Project run script                                   |
| README.md        | The readme file                                      |

## Schedulers

| Scheduler                  | Description                                                                                                                  | Execution Period |
|----------------------------|------------------------------------------------------------------------------------------------------------------------------|------------------|
| `task_scheduler`           | It handles tasks created by operator, splits data when necessary, and generates commands needed by the Job Execution System. | every 12 seconds |
| `status_tracker_scheduler` | It synchronizes task information, including task status and progress information.                                            | every 2 minutes  | 
| `data_processor_scheduler` | It extracts task results from files, and saves the results in the distributed storage.                                       | every 30 minutes |





