CREATE DATABASE IF NOT EXISTS llm_bench_sys;

CREATE TABLE IF NOT EXISTS llm_bench_sys.task_tab(
	`task_id` varchar(64) not null,
    `task_type` varchar(32) not null default 'inference',
    `task_config` json not null,
    `model` text not null,
    `model_config` json not null,
    `status` varchar(16) not null default 'PENDING',
    `progress` json not null,
    `start_at` datetime,
    `stop_at` datetime,
    `created_at` datetime,
    `updated_at` datetime,
    `delete_at` datetime,
    primary key (`task_id`)
);

CREATE TABLE IF NOT EXISTS llm_bench_sys.sub_task_tab(
	`sub_task_id` varchar(64) not null,
    `task_id` varchar(64) not null,
    `sub_task_config` json not null,
    `command` text not null,
    `model` varchar(128) not null default '',
    `model_size` int not null default 0,
    `serial_num` varchar(16) not null default '',
    `output_file_path` varchar(500) not null default '',
    `output_result` json not null,
    `status` varchar(16) not null default 'PENDING',
    `progress` json not null,
    `start_at` datetime,
    `stop_at` datetime,
    `created_at` datetime,
    `updated_at` datetime,
    `delete_at` datetime,
    primary key (`sub_task_id`),
    index `idx_task_id`(`task_id`)
);
