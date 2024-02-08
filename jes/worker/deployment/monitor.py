# coding: UTF-8

import json
import sys

DISABLE = "DISABLE"
GPU_MONITOR_JSON = "/tmp/gpu_monitor.json"

if len(sys.argv) == 3:
    output_file_path = sys.argv[1]
    enable_monitor = sys.argv[2]
else:
    if len(sys.argv) == 2:
        output_file_path = sys.argv[1]
        enable_monitor = "%s" % DISABLE
    else:
        output_file_path = GPU_MONITOR_JSON
        enable_monitor = DISABLE

result = {}


def get_device_info_catch_exception(execute, value):
    try:
        print(execute)
        value = eval(execute)
    except Exception as ex:
        print(f"`{execute}` failed", ex)

    return value


if enable_monitor == "ENABLE":
    try:
        import psutil
        import pynvml

        try:
            pynvml.nvmlInit()
        except Exception as ex:
            raise Exception("nvidia gpu not found.")
        UNIT = 1024 * 1024

        gpuDeriveInfo = get_device_info_catch_exception(
            "pynvml.nvmlSystemGetDriverVersion()", "no")

        gpuDeviceCount = get_device_info_catch_exception(
            "pynvml.nvmlDeviceGetCount()", "no")

        list_gpu_monitor_data = []

        for i in range(gpuDeviceCount):
            gpu_monitor_data = {}

            handle = pynvml.nvmlDeviceGetHandleByIndex(
                i)
            memoryInfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
            gpuName = str(pynvml.nvmlDeviceGetName(handle))
            gpuTemperature = pynvml.nvmlDeviceGetTemperature(handle, 0)
            gpuFanSpeed = get_device_info_catch_exception(
                f"pynvml.nvmlDeviceGetFanSpeed({handle})", 0)
            gpuPowerState = pynvml.nvmlDeviceGetPowerState(handle)
            gpuUtilRate = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
            gpuMemoryRate = pynvml.nvmlDeviceGetUtilizationRates(handle).memory

            gpu_monitor_data.update({
                "gpuId": i,
                "gpuName": gpuName,
                "gpuTotalMemory": memoryInfo.total / UNIT,
                "gpuUsedMemory": memoryInfo.used / UNIT,
                "gpuFreeMemory": memoryInfo.free / UNIT,
                "gpuFreeMemoryRate": memoryInfo.free / memoryInfo.total,
                "gpuTemperature": gpuTemperature,
                "gpuFanSpeed": gpuFanSpeed,
                "gpuPowerState": gpuPowerState,
                "gpuUtilRate": gpuUtilRate,
                "gpuMemoryRate": gpuMemoryRate,
                "gpuMemoryInfoUsedRate": memoryInfo.used / memoryInfo.total
            })
            list_gpu_monitor_data.append(gpu_monitor_data)

        pynvml.nvmlShutdown()

        result.update({
            "code": "success",
            "data": list_gpu_monitor_data
        })

    except Exception as ex:
        result.update({
            "code": "failed",
            "message": str(ex)
        })

    with open(output_file_path, "w") as out:
        out.write(json.dumps(result, indent=4, ensure_ascii=False))
else:
    print("gpu monitor disabled.")
