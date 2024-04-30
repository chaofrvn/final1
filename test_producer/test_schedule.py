import schedule
import time
from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)
# print(current_time > )
print(type(now.hour))
print(now.hour < 1)
print(now.date())
print(type(str(now.date())))
# print()
# def job():
#     print("Running job...")
# # Lập lịch cho công việc chạy mỗi 15 phút từ 0 phút đến 59 phút trong giờ
# schedule.every(10).seconds.do(job)
# def cancel():
#     schedule.cancel_job(job)
# # Lập lịch cho công việc kết thúc vào lúc 17:00 (5 giờ chiều) hàng ngày
# schedule.every().day.at("00:48").do(cancel)

# is_last_job_executed = False

# while not is_last_job_executed:
#     schedule.run_pending()
#     if schedule.next_run() is None:
#         is_last_job_executed = True
#     time.sleep(1)

# # Kết thúc chương trình
# print("Program ended.")
