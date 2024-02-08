from script.helper.metric_helper import MetricStrategy


def check_answer(answer, label, metric: MetricStrategy):
    metric.evaluate(answer, label)
    return metric.metric_result()
