def get_email(keyword):

    emails = {
        "教授": [
            "教授：星期五前記得交 Proposal",
            "教授：下週三下午可以 Meeting"
        ],

        "學校": [
            "學校：研究生獎學金申請開始"
        ]
    }

    return {
        "keyword": keyword,
        "emails" : emails.get(keyword,[])
    }