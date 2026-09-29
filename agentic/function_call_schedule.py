def get_today_schedule(day):
    
    print(f"查詢日期:{day}")
    schedules = {
        "今天": [
            "09:00 上課",
            "14:00 和教授 Meeting",
            "18:00 健身"
        ],

        "明天": [
            "10:00 寫論文",
            "15:00 Meeting",
            "19:00 打球"
        ]
    }
    return {
        "day":day , 
        "events": schedules.get(day,[])
    }