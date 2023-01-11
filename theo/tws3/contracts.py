from ib_insync import contract

contractInfos = [
    {
        "conId": 296574745,
        "exchange": "NYMEX",
    },
    {
        "conId": 297249704,
        "exchange": "IPE",
    },
    {
        "conId": 7089,
        "exchange": "NYSE",
    },
    {
        "conId": 470458975,
        "exchange": "NYSE",
    },
    {
        "conId": 4215217,
        "exchange": "NYSE",
    },
    {
        "conId": 13977,
        "exchange": "NYSE",
    },
    {
        "conId": 6890,
        "exchange": "NYSE",
    },
    {
        "conId": 5684,
        "exchange": "NYSE",
    },
    {
        "conId": 754442,
        "exchange": "NYSE",
    },
    {
        "conId": 10885,
        "exchange": "NYSE",
    },
    {
        "conId": 57698865,
        "exchange": "NYSE",
    },
    {
        "conId": 39118796,
        "exchange": "NYSE",
    },
    {
        "conId": 9831,
        "exchange": "NYSE",
    },
    {
        "conId": 3142097,
        "exchange": "NYSE",
    },
    {
        "conId": 6608450,
        "exchange": "NYSE",
    },
    {
        "conId": 13805,
        "exchange": "NYSE",
    },
    {
        "conId": 75960201,
        "exchange": "NYSE",
    },
    {
        "conId": 418893644,
        "exchange": "NYSE",
    },
    {
        "conId": 10190340,
        "exchange": "NYSE",
    },
    {
        "conId": 415578515,
        "exchange": "NYSE",
    },
    {
        "conId": 495512572,
        "exchange": "CME",
    },
    {
        "conId": 551601503,
        "exchange": "CBOT",
    },
]

contracts = [contract.Contract(**info) for info in contractInfos]
