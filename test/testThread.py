import threading
import time


class StoppableBackgroundTaskScheduler(threading.Thread):
    def __init__(self, interval=5, task=None, log_path='C:/person/background_task_log.txt'):
        super().__init__()
        self.interval = interval
        self.task = task or self.default_task
        self.log_path = log_path
        self.stop_event = threading.Event()
        self.should_stop = False

    def default_task(self):
        return True  # 默认任务总是返回True，表示继续运行

    def write_to_log(self, message):
        with open(self.log_path, 'a') as f:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            f.write(f"{timestamp} - {message}\n")
        print(f"已将消息：{message} 写入日志")

    def run(self):
        while not self.stop_event.is_set() and not self.should_stop:
            start_time = time.time()
            result = self.task()
            elapsed_time = time.time() - start_time
            sleep_time = max(0, self.interval - elapsed_time)
            time.sleep(sleep_time)

            if isinstance(result, bool) and not result:  # 检查任务返回结果是否为False
                self.should_stop = True
                self.write_to_log("任务返回False，即将停止后台调度线程")

            # 如果未停止，则继续循环并写入日志
            else:
                self.write_to_log("执行了一次自定义任务")

    def stop(self):
        self.stop_event.set()


# 定义一个自定义任务，它返回一个布尔值决定是否停止
def custom_conditioned_task(scheduler):
    scheduler.write_to_log("开始执行自定义有时间限制的任务")
    current_time = time.localtime()

    # 检查当前时间是否已超过设定的时间点（10:10:10）
    if current_time.tm_hour == 14 and current_time.tm_min == 50 and current_time.tm_sec >= 35:
        scheduler.write_to_log("已到达设定的停止时间，返回False")
        return False
    else:
        print(f"当前时间：{time.ctime()}，执行自定义有时间限制的任务")
        scheduler.write_to_log("未到达设定的停止时间，继续执行任务")
        return True


if __name__ == '__main__':
    # 创建并启动后台调度线程实例
    scheduler = StoppableBackgroundTaskScheduler(interval=3, task=lambda: custom_conditioned_task(scheduler))
    scheduler.start()

    # 主程序仅启动调度器而不等待其结束
    print("主程序已启动后台调度线程，并即将退出")
